"""
This view contains logic for document import and conversion to PDF.
It handles the conversion of .txt, .odt, and .docx files to PDF format.
Also contains a view to delete the converted PDF file.
"""
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
from odf.text import P, H
from PyPDF2 import PdfFileMerger
import os
import pypandoc
from django.http import FileResponse
from django.conf import settings
from django.core.files.base import ContentFile
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from shared.mixins.evaluator_access_mixin import EvaluatorAccessMixin
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.http import JsonResponse
import tempfile
from docx2pdf import convert
import pythoncom


# Global context variables
TOTAL_STEPS = 8
SHOW_PROGRESS_BAR = True

class DocumentView(LoginRequiredMixin, EvaluatorAccessMixin, View):
    """
    View to open the converted pdf file in the browser.
    Requires the user to be logged in.
    """

    def dispatch(self, request, *args, **kwargs):
        document_id = self.kwargs.get('document_id')
        document = get_object_or_404(UploadedDocument, id=document_id)
        order_id = document.order.id
        self.kwargs['order_id'] = order_id
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, document_id):
        document = get_object_or_404(UploadedDocument, id=document_id)
        response = FileResponse(document.file_path.open('rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{document.file_name}"'
        return response




class DocumentImportView(LoginRequiredMixin, EvaluatorAccessMixin, TemplateView):
    """
    View to handle the import of documents. Handles .txt .odt file conversion to .pdf.
    Requires the user to be logged in and have the appropriate role.
    """
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
        """
        Handle the POST request to upload and process a document.
        """
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
        """
        Convert the uploaded file to a PDF.

        This method handles the conversion of different file types (.odt, .txt, .docx) to PDF format.
        It uses various libraries and tools to achieve this, including pypandoc, ReportLab, and PyPDF2.

        Args:
            file (UploadedFile): The uploaded file to be converted.

        Returns:
            ContentFile: The converted PDF file.

        Raises:
            FileNotFoundError: If the required font file for Lithuanian characters is not found.
            ValueError: If the file type is unsupported.
        """
        file_name, file_extension = os.path.splitext(file.name)
        pdf_buffer = BytesIO()

        # Register a font that supports Lithuanian characters
        font_path = os.path.join(settings.BASE_DIR, 'shared/static/fonts/DejaVuSans.ttf')

        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Font file not found: {font_path}")
        
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))

        if file_extension == '.odt':
            # Handle .odt file conversion

            temp_file_path = os.path.join(settings.MEDIA_ROOT, 'uploaded_documents', f"{file_name}{file_extension}")
            
            with open(temp_file_path, 'wb') as temp_file:

                for chunk in file.chunks():
                    temp_file.write(chunk)

            odt_doc = load_odt(temp_file_path)
            pdf = SimpleDocTemplate(pdf_buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='Lithuanian', fontName='DejaVuSans', fontSize=12))
            elements = []

            for element in odt_doc.getElementsByType(P):
                text_content = self.extract_text_with_formatting(element)
                elements.append(Paragraph(text_content, styles['Lithuanian']))
                elements.append(Spacer(1, 12))

            for element in odt_doc.getElementsByType(H):
                text_content = self.extract_text_with_formatting(element)
                elements.append(Paragraph(text_content, styles['Lithuanian']))
                elements.append(Spacer(1, 12))

            pdf.build(elements)
            pdf_buffer.seek(0)
            pdf_file = ContentFile(pdf_buffer.read(), name=f"{file_name}.pdf")
            os.remove(temp_file_path)

            return pdf_file
        
        elif file_extension == '.docx':
            # Handle .docx file conversion
            pythoncom.CoInitialize()

            try:
                with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as temp_input:

                    for chunk in file.chunks():
                        temp_input.write(chunk)

                    temp_input_path = temp_input.name
                temp_output_path = os.path.join(settings.MEDIA_ROOT, 'uploaded_documents', f"{file_name}.pdf")

                try:
                    convert(temp_input_path, temp_output_path)

                    with open(temp_output_path, 'rb') as pdf_file:
                        pdf_content = pdf_file.read()

                    pdf_file = ContentFile(pdf_content, name=f"{file_name}.pdf")
                    os.remove(temp_input_path)
                    os.remove(temp_output_path)

                    return pdf_file

                except Exception as e:
                    print(f"Conversion failed with docx2pdf: {e}")
                    raise
            finally:
                pythoncom.CoUninitialize()
        
        elif file_extension == '.txt':
            # Handle .txt file conversion

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


    def extract_text_with_formatting(self, element):
        text_content = ""

        for node in element.childNodes:

            if node.nodeType == node.TEXT_NODE:
                text_content += node.data

            elif node.nodeType == node.ELEMENT_NODE:

                if node.tagName == 'text:line-break':
                    text_content += '\n'

                elif node.tagName == 'text:tab':
                    text_content += '⠀ ' * 4

                else:
                    text_content += self.extract_text_with_formatting(node)
                    
        return text_content


    def combine_pdfs(self, pdf_paths, output_path):
        merger = PdfFileMerger()

        for pdf in pdf_paths:
            merger.append(pdf)

        merger.write(output_path)
        merger.close()




class DeleteDocumentView(LoginRequiredMixin, View):
    """
    View to delete the converted .pdf file.
    Requires the user to be logged in.
    """

    def post(self, request, document_id):
        document = get_object_or_404(UploadedDocument, id=document_id)
        document.delete()
        return redirect(request.META.get('HTTP_REFERER', 'modules.evaluator:document_import'))




@method_decorator(csrf_protect, name='dispatch')
class UpdateDocumentCommentView(View):
    """
    View to edit the converted .pdf file's comment.
    Requires the user to be logged in.
    """
        
    def post(self, request, *args, **kwargs):
        document_id = request.POST.get('document_id')
        comment = request.POST.get('comment')
        try:
            document = UploadedDocument.objects.get(id=document_id)
            document.comment = comment
            document.save()
            return JsonResponse({'status': 'success'})
        except UploadedDocument.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Document not found'})