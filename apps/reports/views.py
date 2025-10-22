from django.shortcuts import render, HttpResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
import csv

# Create your views here.

class ReportIndexView(LoginRequiredMixin, TemplateView):
    """Índice Relatórios"""
    template_name = 'reports/report_index.html'


class StockReportView(LoginRequiredMixin, TemplateView):
    """Relatório Estoque"""
    template_name = 'reports/stock_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # TESTE-ESTÁTICO-REPORTS => (Relatório Estoque)
        context['stock_data'] = [
            {'product': 'Produto A', 'stock': 50, 'value': 1250.00},
            {'product': 'Produto B', 'stock': 30, 'value': 1365.00},
        ]
        return context


class MovementReportView(LoginRequiredMixin, TemplateView):
    """Relatório Movimentações"""
    template_name = 'reports/movement_report.html'


def export_stock_csv(request):
    """Export CSV Estoque"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="estoque.csv"'

    # TESTE-ESTÁTICO-CSV-ESTOQUE => (Relatório Estoque)
    writer = csv.writer(response)
    writer.writerow(['Produto', 'Estoque', 'Valor'])
    writer.writerow(['Produto A', '50', '1250.00'])
    writer.writerow(['Produto B', '30', '1365.00'])

    return response


def export_movements_csv(request):
    """Export CSV Movimentos"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="movimentacoes.csv"'

    # TESTE-ESTÁTICO-CSV-MOVIMENTOS => (Relatório Movimentos)
    writer = csv.writer(response)
    writer.writerow(['Data', 'Produto', 'Tipo', 'Quantidade'])
    writer.writerow(['22/10/2025', 'Produto A', 'Entrada', '50'])
    writer.writerow(['21/10/2025', 'Produto B', 'Saída', '15'])

    return response
