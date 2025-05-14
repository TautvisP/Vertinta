"""
This view contains logic for the final step of the evaluation process, generating a final report.
It includes methods for rendering the final report form, saving the report data, and generating the report.
The view also includes a method to check for missing data required to generate the report.
Report generation is handled by rendering LaTeX templates and combining them into a PDF file.
"""
import os
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from shared.mixins.mixins import UserRoleContextMixin
from core.uauth.models import UserMeta
from django.db.models import Q
from modules.orders.models import ObjectMeta, Order, Report, UploadedDocument, NearbyOrganization, ObjectImage, SimilarObject
from django.utils.translation import gettext as _
from modules.evaluator.forms import FinalReportForm, FinalReportEngineeringForm
from modules.orders.forms import ObjectLocationForm, DecorationForm, UtilityForm, CommonInformationForm
from django.template.loader import render_to_string
from django.conf import settings
from django.http import FileResponse
import subprocess
from datetime import datetime
from django.contrib import messages
from shared.mixins.evaluator_access_mixin import EvaluatorAccessMixin
from modules.orders.utils import create_report_submission_notification
from weasyprint import HTML, CSS
from io import BytesIO
from django.core.files.base import ContentFile

# Global context variables
TOTAL_STEPS = 8
SHOW_PROGRESS_BAR = True


class GenerateReportView(LoginRequiredMixin, EvaluatorAccessMixin, UserRoleContextMixin, TemplateView):
    """
    View to generate a final report for an order.
    Requires the user to be logged in and have the appropriate role.
    """
    template_name = "generate_report.html"
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'
    user_meta = UserMeta


    def get_context_data(self, **kwargs):
        """
        Get the context data for the template.
        
        This method retrieves the order, object, and client data, and adds it to the context.
        It also includes additional context variables such as the phone number, order ID, 
        primary key, progress bar visibility, current step, and total steps.
        """
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
        context['current_step'] = 8
        context['total_steps'] = TOTAL_STEPS

        # Get or create the report instance
        report, created = Report.objects.get_or_create(order=order)
        context['final_report_form'] = FinalReportForm(instance=report)
        context['missing_data'] = self.check_missing_data(order)
        return context


    def post(self, request, *args, **kwargs):
        """
        Handle the POST request to generate the final report.
        
        This method processes the final report form, generates the report, and saves it.
        If the form is valid, it generates the report and redirects to the success URL.
        If the form is invalid, it renders the form with errors.
        """
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        obj = order.object
        client = order.client

        report, created = Report.objects.get_or_create(order=order)
        final_report_form = FinalReportForm(request.POST, instance=report)

        if final_report_form.is_valid():
            final_report_form.save()
            missing_data = self.check_missing_data(order)

            if missing_data:
                messages.warning(request, f"Trūksta duomenų: {', '.join(missing_data)}")
                return redirect('modules.evaluator:generate_report', order_id=order_id, pk=obj.pk)

            return redirect('modules.evaluator:final_report_engineering', order_id=order_id, pk=obj.pk)

        context = self.get_context_data(**kwargs)
        context['final_report_form'] = final_report_form
        return self.render_to_response(context)
    

    def check_missing_data(self, order):
        """
        Check for missing data required to generate the final report.

        This method validates the data for the order and its associated object to ensure that all
        necessary information is present before generating the final report. It checks the validity
        of forms related to location, decoration, utility, and common information. If any of these
        forms are invalid, it adds a description of the missing data to the `missing_data` list.
        """
        missing_data = []

        if not order.object:
            missing_data.append("1-ame žingsnyje nepilnai užpildyti vertinamo objekto duomenys")

        if not ObjectMeta.objects.filter(
            Q(ev_object=order.object, meta_key__startswith='garage_') |
            Q(ev_object=order.object, meta_key__startswith='shed_') |
            Q(ev_object=order.object, meta_key__startswith='gazebo_')
        ).exists():
            missing_data.append("2-ame žingsnyje nepridėti papildomi statiniai")

        if ObjectImage.objects.filter(object=order.object).count() == 0:
            missing_data.append("4-ame žingsnyje nėra vertinamo objekto nuotraukų")

        if not SimilarObject.objects.filter(original_object=order.object).exists():
            missing_data.append("5-ame žingsnyje nėra panašių objektų paieška")

        if not UploadedDocument.objects.filter(order=order).exists():
            missing_data.append("6-ame žingsnyje nėra pridėtų dokumentų")

        if not NearbyOrganization.objects.filter(object=order.object).exists():
            missing_data.append("7-ame žingsnyje nėra netoliese esančių įstaigų")

        # Check if forms are fully populated
        location_form = ObjectLocationForm(data=self.get_form_data(order.object, ObjectLocationForm))
        decoration_form = DecorationForm(data=self.get_form_data(order.object, DecorationForm))
        utility_form = UtilityForm(data=self.get_form_data(order.object, UtilityForm))
        common_info_form = CommonInformationForm(data=self.get_form_data(order.object, CommonInformationForm))

        if not location_form.is_valid():
            missing_data.append("Lokacijos duomenys")

        if not decoration_form.is_valid():
            missing_data.append("Apdailos duomenys")

        if not utility_form.is_valid():
            missing_data.append("Komunalinių paslaugų duomenys")

        if not common_info_form.is_valid():
            missing_data.append("Bendros informacijos duomenys")

        return missing_data

    def get_form_data(self, obj, form_class):
        form = form_class()
        form_data = {}
        for field in form:
            form_data[field.name] = getattr(obj, field.name, None)
        return form_data




class FinalReportEngineeringView(LoginRequiredMixin, EvaluatorAccessMixin, UserRoleContextMixin, TemplateView):
    """
    View to handle the final report engineering step in the report generation process.
    Requires the user to be logged in and have the appropriate role.
    """
    template_name = "final_report_engineering.html"
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'
    user_meta = UserMeta
    
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
        context['current_step'] = 8
        context['total_steps'] = TOTAL_STEPS

        # Get or create the report instance
        report, created = Report.objects.get_or_create(order=order)
        context['final_report_text_form'] = FinalReportEngineeringForm(instance=report)
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle the POST request to save the final report engineering data and generate report.
        """
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        report, created = Report.objects.get_or_create(order=order)

        final_report_text_form = FinalReportEngineeringForm(request.POST, instance=report)

        if final_report_text_form.is_valid():
            try:
                report = final_report_text_form.save(commit=True)
                success, message = PDFReportGenerator.generate_report(order, report, request)

                if success:
                    messages.success(request, message)
                    return redirect('modules.orders:evaluator_order_list')
                else:
                    messages.error(request, message)

            except Exception as e:
                print(f"Error generating report: {str(e)}")
                messages.error(request, f"Klaida generuojant ataskaitą: {str(e)}")
        else:
            print(f"Form errors: {final_report_text_form.errors}")

            for field, errors in final_report_text_form.errors.items():

                for error in errors:
                    messages.error(request, f"{field}: {error}")

        context = self.get_context_data(**kwargs)
        context['final_report_text_form'] = final_report_text_form
        return self.render_to_response(context)



class PDFReportGenerator:

    @staticmethod
    def get_image_file_url(image_field):
        if not image_field:
            return ''
        abs_path = os.path.abspath(os.path.join(settings.MEDIA_ROOT, image_field.name))
        # Convert backslashes to forward slashes for file URLs
        file_url = 'file:///' + abs_path.replace('\\', '/')
        return file_url


    @staticmethod
    def generate_report(order, report, request):
        """
        Generate a PDF report for the given order and report using WeasyPrint.
        Returns (success, message) tuple.
        """
        try:
            obj = order.object
            client = order.client
            user_meta = UserMeta

            if not PDFReportGenerator.check_report_data_complete(report):
                return False, _("Nepavyko sugeneruoti ataskaitos - trūksta būtinų duomenų.")

            phone_number = user_meta.get_meta(client, 'phone_num')
            meta_data = ObjectMeta.objects.filter(ev_object=obj)
            meta_dict = {meta.meta_key: meta.meta_value for meta in meta_data}
            images = []

            for img in obj.images.all():
                img_dict = {
                    'comment': img.comment,
                    'category': img.category,
                    'file_url': PDFReportGenerator.get_image_file_url(img.image),
                    'annotations': []
                }

                for annotation in img.annotations.all():
                    annotation_dict = {
                        'annotation_text': annotation.annotation_text,
                        'annotation_image_url': PDFReportGenerator.get_image_file_url(annotation.annotation_image) if annotation.annotation_image else '',
                        'x_coordinate': annotation.x_coordinate,
                        'y_coordinate': annotation.y_coordinate,
                    }
                    img_dict['annotations'].append(annotation_dict)

                images.append(img_dict)
            
            # Create HTML context for rendering the template
            html_context = {
                'report_title': 'Turto Vertinimo Ataskaita',
                'report_date': datetime.now().strftime('%Y-%m-%d'),
                'client_first_name': client.first_name,
                'client_last_name': client.last_name,
                'customer_phone': phone_number,
                'property_street': obj.street,
                'property_house_no': obj.house_no,
                'property_municipality': obj.municipality,
                'evaluator_first_name': request.user.first_name,
                'evaluator_last_name': request.user.last_name,
                'company_name': 'Vertinta',
                'images': images,
                'engineering': report.engineering,
                'addictions': report.addictions,
                'floor_plan': report.floor_plan,
                'district': report.district,
                'conclusion': report.conclusion,
                'valuation_methodology': report.valuation_methodology,
                'media_url': settings.MEDIA_URL,
                'meta_data': meta_dict,
            }

            # Render HTML template
            html_content = render_to_string('report/full_report.html', html_context)

            debug_html_path = os.path.join(settings.MEDIA_ROOT, f'report_{order.id}_debug.html')
            with open(debug_html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            # Generate PDF using WeasyPrint
            pdf_file = BytesIO()

            css_path = os.path.join(settings.BASE_DIR, 'modules', 'evaluator', 'templates', 'report', 'report.css')
            css = CSS(filename=css_path) if os.path.exists(css_path) else None

            HTML(string=html_content, base_url=settings.MEDIA_ROOT).write_pdf(pdf_file, stylesheets=[css] if css else None)
            pdf_bytes = pdf_file.getvalue()
            pdf_file.close()

            # Save PDF to report object
            report.report_file.save(f'report_{order.id}.pdf', ContentFile(pdf_bytes))

            report.status = 'pending'
            report.save()
            PDFReportGenerator.notify_agency(order, request)
            create_report_submission_notification(report, request.user)

            return True, _("Ataskaita sėkmingai sugeneruota ir išsiųsta agentūrai patvirtinimui.")

        except Exception as e:
            import traceback
            print(f"Error generating PDF report: {str(e)}")
            print(traceback.format_exc())
            return False, f"Klaida generuojant ataskaitą: {str(e)}"


    @staticmethod
    def check_report_data_complete(report):
        """
        Check if all required report data is present.
        """
        required_fields = [
            'engineering', 'addictions', 'floor_plan', 
            'district', 'conclusion', 'valuation_methodology'
        ]
        
        for field in required_fields:
            value = getattr(report, field, None)
            if not value:
                return False
        
        return True

    
    @staticmethod
    def notify_agency(order, request):
        """
        Send notification to agency about new report requiring confirmation.
        """
        from django.urls import reverse
        
        if not order.agency:
            return
            
        agency = order.agency
        client = order.client
        
        subject = _("Naujos ataskaitos patvirtinimas reikalingas")
        message = f"""
Sveiki,

Vertintojas {order.evaluator.get_full_name()} sugeneravo naują ataskaitą užsakymui #{order.id}.
Kliento informacija: {client.get_full_name()}
Objekto informacija: {order.object.object_type} {order.object.street} {order.object.house_no}

Prašome peržiūrėti ir patvirtinti ataskaitą, kad ji būtų prieinama klientui.
Galite peržiūrėti ataskaitą paspaudę šią nuorodą: 
{request.build_absolute_uri(reverse('modules.agency:review_report', args=[order.id]))}

Ačiū,
Nekilnojamo Turto Vertinimo Sistema
        """
        
        try:
            print("\n" + "="*80)
            print("AGENCY NOTIFICATION EMAIL")
            print("="*80)
            print(f"To: {agency.email}")
            print(f"Subject: {subject}")
            print(f"Message: {message}")
            print("="*80 + "\n")
            
            # email = EmailMessage(
            #     subject=subject,
            #     body=message,
            #     from_email=settings.DEFAULT_FROM_EMAIL,
            #     to=[agency.email],
            # )
            # email.send()
        except Exception as e:
            print(f"Failed to send agency notification: {e}")