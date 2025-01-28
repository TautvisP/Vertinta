import os
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from shared.mixins.mixins import UserRoleContextMixin
from core.uauth.models import UserMeta
from modules.orders.models import ObjectMeta
from modules.orders.models import Object, Order, Report
from django.utils.translation import gettext as _
from modules.evaluator.forms import FinalReportForm, FinalReportEngineeringForm
from django.template.loader import render_to_string
from django.conf import settings
from django.http import FileResponse
import subprocess
from datetime import datetime



# Global context variables
TOTAL_STEPS = 8
SHOW_PROGRESS_BAR = True


class GenerateReportView(LoginRequiredMixin, UserRoleContextMixin, TemplateView):
    template_name = "generate_report.html"
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
        context['final_report_form'] = FinalReportForm(instance=report)
        return context

    def post(self, request, *args, **kwargs):
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        obj = order.object
        client = order.client

        report, created = Report.objects.get_or_create(order=order)
        final_report_form = FinalReportForm(request.POST, instance=report)
        if final_report_form.is_valid():
            final_report_form.save()

            # Redirect to the next step
            return redirect('modules.evaluator:final_report_engineering', order_id=order_id, pk=obj.pk)

        context = self.get_context_data(**kwargs)
        context['final_report_form'] = final_report_form
        return self.render_to_response(context)

class FinalReportEngineeringView(LoginRequiredMixin, UserRoleContextMixin, TemplateView):
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
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        obj = order.object
        client = order.client

        report, created = Report.objects.get_or_create(order=order)
        final_report_text_form = FinalReportEngineeringForm(request.POST, instance=report)
        if final_report_text_form.is_valid():
            final_report_text_form.save()

            if 'generate' in request.POST:
                # Redirect to the generate report view
                return redirect('modules.evaluator:generate_report', order_id=order_id, pk=obj.pk)

        context = self.get_context_data(**kwargs)
        context['final_report_text_form'] = final_report_text_form
        return self.render_to_response(context)
    




class GenerateLatexReportView(LoginRequiredMixin, UserRoleContextMixin, View):
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'
    user_meta = UserMeta

    def post(self, request, *args, **kwargs):
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        obj = order.object
        client = order.client
        report = get_object_or_404(Report, order=order)

        images = obj.images.all()

        # Gather metadata for the object
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
            'customer_name': report.customer_name,
            'customer_surname': report.customer_surname,
            'customer_phone': report.customer_phone,
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

        latex_file_path = os.path.join(settings.MEDIA_ROOT, 'report.tex')
        with open(latex_file_path, 'w') as latex_file:
            latex_file.write(latex_content)

        pdf_file_path = os.path.join(settings.MEDIA_ROOT, 'report.pdf')
        subprocess.run(['pdflatex', '-output-directory', settings.MEDIA_ROOT, latex_file_path])

        return FileResponse(open(pdf_file_path, 'rb'), content_type='application/pdf', as_attachment=True, filename='report.pdf')