from admin_tools.dashboard import modules, Dashboard
from admin_tools.utils import get_admin_site_name
from django.urls import reverse

class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for the admin site.
    """

    def init_with_context(self, context):
        site_name = get_admin_site_name(context)

        # Quick links module
        self.children.append(modules.LinkList(
            _('Quick links'),
            layout='inline',
            draggable=False,
            deletable=False,
            collapsible=False,
            children=[
                [_('Add new Cotacao'), reverse('admin:cotacao_cotacao_add')],
                [_('Manage Cotacoes'), reverse('admin:cotacao_cotacao_changelist')],
                [_('Add new Departamento'), reverse('admin:cotacao_departamento_add')],
                [_('Manage Departamentos'), reverse('admin:cotacao_departamento_changelist')],
            ]
        ))

        # Latest Cotacoes module
        self.children.append(modules.ModelList(
            _('Recent Cotacoes'),
            models=('cotacao.models.Cotacao',),
            limit=5,
            collapsible=False,
        ))

        # Items in Cotacoes module
        self.children.append(modules.ModelList(
            _('Items in Cotacoes'),
            models=('cotacao.models.ItemCotacao',),
            limit=5,
            collapsible=False,
        ))

        # Example: Adding a simple graph (requires integration with a graphing library or custom implementation)
        # self.children.append(modules.Graph(
        #     title=_('Cotacao Status Graph'),
        #     graph_url=reverse('admin:cotacao_graph')
        # ))

# Replace the default dashboard with the custom one
from admin_tools.dashboard import DefaultIndexDashboard

admin_tools_dashboard = DefaultIndexDashboard
admin_tools_dashboard.__bases__ = (CustomIndexDashboard,)
