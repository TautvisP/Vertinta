from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from shared.mixins.mixins import UserRoleContextMixin
from core.uauth.models import UserMeta
from modules.orders.models import Object, Order, UploadedDocument
from modules.evaluator.forms import TextFileUploadForm
from django.utils.translation import gettext as _
from docx import Document as DocxDocument
from odf.opendocument import load as load_odt
from odf.text import P
from PyPDF2 import PdfFileMerger
import os
import subprocess
import pypandoc
from django.http import FileResponse
from django.conf import settings
from django.core.files.base import ContentFile
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# Global context variables
TOTAL_STEPS = 8
SHOW_PROGRESS_BAR = True

class DocumentView(LoginRequiredMixin, View):
    
    def get(self, request, document_id):
        document = get_object_or_404(UploadedDocument, id=document_id)
        response = FileResponse(document.file_path.open('rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{document.file_name}"'
        return response
    



class DocumentImportView(LoginRequiredMixin, UserRoleContextMixin, TemplateView):
    model = Object
    user_meta = UserMeta
    template_name = "document_addition.html"
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        obj = order.object
        client = order.client
        phone_number = self.user_meta.get_meta(client, 'phone_num')
        context['order'] = order
        context['object'] = obj
        context['client'] = client
        context['phone_number'] = phone_number
        context['order_id'] = self.kwargs['order_id']
        context['pk'] = self.kwargs['pk']
        context['show_progress_bar'] = SHOW_PROGRESS_BAR
        context['current_step'] = 6
        context['total_steps'] = TOTAL_STEPS
        context['form'] = TextFileUploadForm()
        context['uploaded_documents'] = UploadedDocument.objects.filter(order=order)
        return context


    def post(self, request, *args, **kwargs):
        print("POST request received")
        form = TextFileUploadForm(request.POST, request.FILES)

        if form.is_valid():
            print("Form is valid")
            file = form.cleaned_data['file']
            comment = form.cleaned_data['comment']

            try:
                pdf_file = self.convert_to_pdf(file)
                print("File converted to PDF")

            except Exception as e:
                print(f"Error converting file to PDF: {e}")
                return self.render_to_response(self.get_context_data(**kwargs))
            
            order_id = self.kwargs.get('order_id')
            order = get_object_or_404(Order, id=order_id)
            uploaded_document = UploadedDocument.objects.create(
                order=order,
                file_name=pdf_file.name,
                file_path=pdf_file,
                comment=comment
            )
            print("UploadedDocument instance created")
            return redirect('modules.evaluator:document_import', order_id=order_id, pk=self.kwargs['pk'])
        
        else:
            print("Form is invalid")

        return self.render_to_response(self.get_context_data(form=form))


    def convert_to_pdf(self, file):
        file_name, file_extension = os.path.splitext(file.name)
        pdf_buffer = BytesIO()

        # Register a font that supports Lithuanian characters
        font_path = os.path.join(settings.BASE_DIR, 'shared/static/fonts/DejaVuSans.ttf')

        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Font file not found: {font_path}")
        
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))

        if file_extension == '.docx':
            temp_file_path = os.path.join(settings.MEDIA_ROOT, 'uploaded_documents', f"{file_name}{file_extension}")
            
            with open(temp_file_path, 'wb') as temp_file:

                for chunk in file.chunks():
                    temp_file.write(chunk)

            pypandoc.download_pandoc()

            # Convert the file to PDF using pypandoc with pdflatex as the PDF engine
            pdf_path = os.path.join(settings.MEDIA_ROOT, 'uploaded_documents', f"{file_name}.pdf")

            try:
                pypandoc.convert_file(temp_file_path, 'pdf', outputfile=pdf_path, extra_args=['--pdf-engine=pdflatex'])
                print(f"Converted {temp_file_path} to {pdf_path}")

            except Exception as e:
                print(f"Conversion failed: {e}")
                raise

            with open(pdf_path, 'rb') as pdf_file:
                pdf_content = pdf_file.read()

            pdf_file = ContentFile(pdf_content, name=f"{file_name}.pdf")

            os.remove(temp_file_path)

            return pdf_file
        
        elif file_extension == '.odt':
            temp_file_path = os.path.join(settings.MEDIA_ROOT, 'uploaded_documents', f"{file_name}{file_extension}")
            
            with open(temp_file_path, 'wb') as temp_file:

                for chunk in file.chunks():
                    temp_file.write(chunk.replace(b'\t', b'    '))

            pdf_path = os.path.join(settings.MEDIA_ROOT, 'uploaded_documents', f"{file_name}.pdf")

            #Using unoconv to convert the file to PDF
            try:
                result = subprocess.run(
                    [
                        "unoconv",
                        "-f",
                        "pdf",
                        "-o",
                        pdf_path,
                        temp_file_path
                    ],
                    check=True,
                    capture_output=True,
                    text=True
                )
                print(f"unoconv output: {result.stdout}")
                print(f"unoconv errors: {result.stderr}")

            except subprocess.CalledProcessError as e:
                print(f"unoconv conversion failed: {e.stderr}")
                raise

            with open(pdf_path, 'rb') as pdf_file:
                pdf_content = pdf_file.read()

            os.remove(temp_file_path)

            return ContentFile(pdf_content, name=f"{file_name}.pdf")
        
        elif file_extension == '.txt':
            content = file.read().decode('utf-8')
            pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
            pdf.setFont("DejaVuSans", 12)
            text_object = pdf.beginText(40, 750)
            text_object.setTextOrigin(40, 750)
            text_object.setFont("DejaVuSans", 12)

            for line in content.splitlines():
                text_object.textLine(line.replace('\t', '    '))

            pdf.drawText(text_object)
            pdf.save()
            pdf_buffer.seek(0)
            pdf_file = ContentFile(pdf_buffer.read(), name=f"{file_name}.pdf")
            return pdf_file
        
        else:
            raise ValueError("Unsupported file type")


    def combine_pdfs(self, pdf_paths, output_path):
        merger = PdfFileMerger()

        for pdf in pdf_paths:
            merger.append(pdf)

        merger.write(output_path)
        merger.close()




class DeleteDocumentView(LoginRequiredMixin, View):

    def post(self, request, document_id):
        document = get_object_or_404(UploadedDocument, id=document_id)
        document.delete()
        return redirect(request.META.get('HTTP_REFERER', 'modules.evaluator:document_import'))