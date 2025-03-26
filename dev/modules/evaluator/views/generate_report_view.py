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
        
        # Create the form with the POST data and the report instance
        final_report_text_form = FinalReportEngineeringForm(request.POST, instance=report)
        
        if final_report_text_form.is_valid():
            try:
                # Save the form data explicitly
                report = final_report_text_form.save(commit=True)
                print(f"Saved report data: engineering={report.engineering}, addictions={report.addictions}, floor_plan={report.floor_plan}, district={report.district}, conclusion={report.conclusion}, valuation_methodology={report.valuation_methodology}")
                
                # Generate report using the utility class
                success, message = LaTeXReportGenerator.generate_report(order, report, request)
                
                if success:
                    messages.success(request, message)
                    # Redirect to the evaluator order list on success
                    return redirect('modules.orders:evaluator_order_list')
                else:
                    messages.error(request, message)
                    
            except Exception as e:
                print(f"Error generating report: {str(e)}")
                messages.error(request, f"Klaida generuojant ataskaitą: {str(e)}")
        else:
            # If the form is invalid, log the errors
            print(f"Form errors: {final_report_text_form.errors}")
            for field, errors in final_report_text_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        
        # If form is invalid or there was an error, redisplay with errors
        context = self.get_context_data(**kwargs)
        context['final_report_text_form'] = final_report_text_form
        return self.render_to_response(context)



class LaTeXReportGenerator:
    """
    Utility class for generating LaTeX reports.
    This class handles the actual report generation logic,
    separating it from the view handling.
    """
    @staticmethod
    def generate_report(order, report, request):
        """
        Generate a LaTeX report for the given order and report.
        Returns (success, message) tuple.
        """
        try:
            obj = order.object
            client = order.client
            user_meta = UserMeta
            
            # Check if report data is complete
            if not LaTeXReportGenerator.check_report_data_complete(report):
                return False, _("Nepavyko sugeneruoti ataskaitos - trūksta būtinų duomenų.")
            
            # Get metadata and prepare context
            phone_number = user_meta.get_meta(client, 'phone_num')
            images = obj.images.all()
            meta_data = ObjectMeta.objects.filter(ev_object=obj)
            meta_dict = {meta.meta_key: meta.meta_value for meta in meta_data}
            
            # Context data for LaTeX templates
            context = {
                'report_title': 'Turto Vertinimo Ataskaita',
                'property_id': obj.id,
                'property_street': obj.street,
                'property_house_no': obj.house_no,
                'property_municipality': obj.municipality,
                'client_first_name': client.first_name,
                'client_last_name': client.last_name,
                'company_name': 'Vertinta',
                'manager_first_name': 'Vadovas',
                'manager_last_name': 'Pavardė',
                'evaluator_first_name': request.user.first_name,
                'evaluator_last_name': request.user.last_name,
                'report_date': datetime.now().strftime('%Y-%m-%d'),
                'customer_name': client.first_name,
                'customer_surname': client.last_name,
                'customer_phone': phone_number,
                'visit_date': report.visit_date,
                'description': report.description,
                'engineering': report.engineering,
                'addictions': report.addictions,
                'floor_plan': report.floor_plan,
                'district': report.district,
                'conclusion': report.conclusion,
                'valuation_methodology': report.valuation_methodology,
                'images': images,
                'meta_data': meta_dict,
                'latitude': obj.latitude,
                'longitude': obj.longitude,
            }
            
            # Render LaTeX templates
            report_title = render_to_string('report/report_title.tex', context)
            report_property = render_to_string('report/report_property.tex', context)
            report_client = render_to_string('report/report_client.tex', context)
            report_company = render_to_string('report/report_company.tex', context)
            report_details = render_to_string('report/report_details.tex', context)
            report_gallery = render_to_string('report/report_gallery.tex', context)
            report_regulation = render_to_string('report/static_text/report_evaluation_regulation.tex', context)
            report_general = render_to_string('report/static_text/report_general_provisions.tex', context)
            report_rights = render_to_string('report/static_text/report_rights.tex', context)
            report_terms = render_to_string('report/static_text/term_explanation.tex', context)
            
            # Combine LaTeX templates
            latex_content = f"""
            \\documentclass{{article}}
            \\usepackage[utf8]{{inputenc}}
            \\usepackage[lithuanian]{{babel}}
            \\usepackage[T1]{{fontenc}}
            \\usepackage{{graphicx}}
            \\usepackage{{tikz}}
            \\usetikzlibrary{{backgrounds}}
            
            \\pgfdeclarelayer{{background}}
            \\pgfdeclarelayer{{foreground}}
            \\pgfsetlayers{{background,main,foreground}}
            
            \\begin{{document}}
            \\sloppy
            {report_title}
            {report_terms}
            {report_regulation}
            {report_general}
            {report_rights}
            {report_client}
            {report_property}
            {report_company}
            {report_details}
            {report_gallery}
            \\end{{document}}
            """
            
            # Write LaTeX file
            latex_file_path = os.path.join(settings.MEDIA_ROOT, f'report_{order.id}.tex')
            with open(latex_file_path, 'w') as latex_file:
                latex_file.write(latex_content)
            
            # Generate PDF
            pdf_file_path = os.path.join(settings.MEDIA_ROOT, f'report_{order.id}.pdf')
            subprocess.run(['pdflatex', '-output-directory', settings.MEDIA_ROOT, latex_file_path])
            
            # Save PDF to report object
            report_file_generated = False
            try:
                with open(pdf_file_path, 'rb') as pdf_file:
                    report.report_file.save(f'report_{order.id}.pdf', pdf_file)
                    report_file_generated = True
            except Exception as e:
                print(f"Error saving PDF: {str(e)}")
                return False, f"Nepavyko išsaugoti ataskaitos failo: {str(e)}"
            
            if report_file_generated:
                report.status = 'pending'
                report.save()
                
                # Notify agency
                LaTeXReportGenerator.notify_agency(order, request)
                
                return True, _("Ataskaita sėkmingai sugeneruota ir išsiųsta agentūrai patvirtinimui.")
            else:
                return False, _("Nepavyko sugeneruoti ataskaitos.")
                
        except Exception as e:
            print(f"Error generating report: {str(e)}")
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
            # Print to console for development
            print("\n" + "="*80)
            print("AGENCY NOTIFICATION EMAIL")
            print("="*80)
            print(f"To: {agency.email}")
            print(f"Subject: {subject}")
            print(f"Message: {message}")
            print("="*80 + "\n")
            
            # In production you would send the actual email
            # email = EmailMessage(
            #     subject=subject,
            #     body=message,
            #     from_email=settings.DEFAULT_FROM_EMAIL,
            #     to=[agency.email],
            # )
            # email.send()
        except Exception as e:
            print(f"Failed to send agency notification: {e}")