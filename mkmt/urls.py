from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.about, name='About'),
    url(r'^break_my_team', views.break_my_team, name='brmt (Weakness Checker)'),
    url(r'^mcr_generator', views.mcr_generator, name='Metagame Coverage Ranking List'),
    url(r'^Pokemon_data', views.Pokemon_data, name='Pokemon Data'),
    url(r'^partner_finder', views.partner_finder, name='Partner Finder'),
    url(r'^core_builder', views.core_builder, name='Core Builder'),
    url(r'^team_generator', views.team_generator, name='Team Generator'),
    url(r'^team_completer', views.team_completer, name='Team Completer'),
    url(r'^replacement_suggestor', views.replacement_suggestor, name='Replacement Suggestor'),
    url(r'^custom_generator', views.custom_generator, name='Custom Generator'),
    url(r'^counterteam_generator', views.counterteam_generator, name='Counterteam Generator'),
    url(r'^team_comparer', views.team_comparer, name='Team Comparer'),
    url(r'^check_map', views.check_map, name='Check Map'),
    url(r'^set_usage_stats', views.set_usage_stats, name='Show Usage Stats By Set'),
    url(r'^how_to_update', views.how_to_update, name='How To Update Or Modify'),
    url(r'^credits', views.credits, name='Credits'),
]