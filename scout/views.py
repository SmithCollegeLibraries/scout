from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie
from scout.dao.space import (get_spot_by_id, get_filtered_spots,
                             get_period_filter, get_spots_by_filter,
                             group_spots_by_building, get_building_list,
                             validate_detail_info, get_random_limit_from_spots,
                             post_occupancy)
from scout.dao.image import get_spot_image, get_item_image
from scout.dao.item import (get_item_by_id, get_filtered_items, get_item_count)

from django.views.generic.base import TemplateView, TemplateResponse

# using red square as the default center
DEFAULT_LAT = 42.319862
DEFAULT_LON = -72.638693


CAMPUS_LOCATIONS = {
    "smith": {"latitude": 42.319862, "longitude": -72.638693},
}


def validate_campus_selection(function):
    def wrap(request, *args, **kwargs):
        if settings.CAMPUS_URL_LIST and isinstance(settings.CAMPUS_URL_LIST,
                                                   list):
            campuses = settings.CAMPUS_URL_LIST
        else:
            raise ImproperlyConfigured("Must define a CAMPUS_URL_LIST"
                                       "of type list in the settings")
        if kwargs['campus'] in campuses:
            return function(request, *args, **kwargs)
        else:
            raise Http404
    return wrap


# discover
class DiscoverView(TemplateView):
    template_name = "404.html"

    @validate_campus_selection
    def get_context_data(self, **kwargs):
        self.template_name = kwargs['template_name']
        context = {"campus": kwargs['campus'],
                   "campus_locations": CAMPUS_LOCATIONS,
                   "random_cards": ["studyopen", "studylounge", "studyareas", "studyrooms", "studylabs", "studysilent", "studynaturallight"]}
        return context


class DiscoverCardView(TemplateView):
    template_name = "404.html"

    @validate_campus_selection
    def get_context_data(self, **kwargs):
        self.template_name = kwargs['template_name']
        # Will figure this out later
        lat = self.request.GET.get('latitude', None)
        lon = self.request.GET.get('longitude', None)

        # Change it per need basis.
        discover_categories = {
            "studyopen": {
                "title": "Open Spaces",
                "spot_type": "study",
                "filter_url": "type0=open",
                "filter": [
                    ('limit', 5),
                    ('center_latitude', lat if lat else DEFAULT_LAT),
                    ('center_longitude', lon if lon else DEFAULT_LON),
                    ('distance', 100000),
                    ('type', 'open')
                    ]
            },
            "studylounge": {
                "title": "Lounges",
                "spot_type": "study",
                "filter_url": "type0=lounge",
                "filter": [
                    ('limit', 5),
                    ('center_latitude', lat if lat else DEFAULT_LAT),
                    ('center_longitude', lon if lon else DEFAULT_LON),
                    ('distance', 100000),
                    ('type', 'lounge')
                    ]
            },
            "studyareas": {
                "title": "Study Areas",
                "spot_type": "study",
                "filter_url": "type0=study_area",
                "filter": [
                    ('limit', 5),
                    ('center_latitude', lat if lat else DEFAULT_LAT),
                    ('center_longitude', lon if lon else DEFAULT_LON),
                    ('distance', 100000),
                    ('type', 'study_area')
                    ]
            },
            "studyrooms": {
                "title": "Study Rooms",
                "spot_type": "study",
                "filter_url": "type0=study_room",
                "filter": [
                    ('limit', 5),
                    ('center_latitude', lat if lat else DEFAULT_LAT),
                    ('center_longitude', lon if lon else DEFAULT_LON),
                    ('distance', 100000),
                    ('type', 'study_room')
                ]
            },
            "studylabs": {
                "title": "Computer Labs",
                "spot_type": "study",
                "filter_url": "type0=computer_lab",
                "filter": [
                    ('limit', 5),
                    ('center_latitude', lat if lat else DEFAULT_LAT),
                    ('center_longitude', lon if lon else DEFAULT_LON),
                    ('distance', 100000),
                    ('type', 'computer_lab')
                ]
            },
            "studysilent": {
                "title": "Silent Spaces",
                "spot_type": "study",
                "filter_url": "noise0=silent",
                "filter": [
                    ('limit', 5),
                    ('center_latitude', lat if lat else DEFAULT_LAT),
                    ('center_longitude', lon if lon else DEFAULT_LON),
                    ('distance', 100000),
                    ('extended_info:noise_level', 'silent')
                ]
            },
            "studynaturallight": {
                "title": "Natural Light",
                "spot_type": "study",
                "filter_url": "lighting0=has_natural_light",
                "filter": [
                    ('limit', 5),
                    ('center_latitude', lat if lat else DEFAULT_LAT),
                    ('center_longitude', lon if lon else DEFAULT_LON),
                    ('distance', 100000),
                    ('extended_info:has_natural_light', 'true')
                ]
            },
        }

        try:
            discover_data = discover_categories[kwargs['discover_category']]
        except KeyError:
            self.response_class = Response404
            self.template_name = "404.html"
            return custom_404_context(kwargs["campus"])

        discover_data["filter"].append(('extended_info:campus',
                                        kwargs['campus']))

        spots = get_spots_by_filter(discover_data["filter"])
        if len(spots) == 0:
            self.response_class = Response404
            self.template_name = "404.html"
            return custom_404_context(kwargs["campus"])
        if kwargs['discover_category'] in ['foodrandom', 'studyrandom']:
            spots = get_random_limit_from_spots(spots, 5)

        context = {
            "spots": spots,
            "campus": kwargs['campus'],
            "card_title": discover_data["title"],
            "spot_type": discover_data["spot_type"],
            "card_filter_url": discover_data["filter_url"]
        }
        return context


# food
class FoodListView(TemplateView):
    template_name = "404.html"

    @validate_campus_selection
    def get_context_data(self, **kwargs):
        self.template_name = kwargs['template_name']
        spots = get_filtered_spots(self.request, kwargs['campus'], "food")
        context = {"spots": spots,
                   "campus": kwargs['campus'],
                   "count": len(spots),
                   "app_type": 'food',
                   "campus_locations": CAMPUS_LOCATIONS}
        return context


class HybridFoodListView(TemplateView):
    template_name = "404.html"

    @validate_campus_selection
    def get_context_data(self, **kwargs):
        self.template_name = kwargs['template_name']

        # get user lat/lng from query params
        lat = self.request.GET.get('h_lat', DEFAULT_LAT)
        lng = self.request.GET.get('h_lng', DEFAULT_LON)

        spots = get_spots_by_filter([
            ('extended_info:app_type', 'food'),
            ('extended_info:campus', kwargs['campus']),
            ('limit', 10),
            ('center_latitude', lat),
            ('center_longitude', lng),
            ('distance', 100000)
        ])
        context = {"spots": spots,
                   "campus": kwargs['campus'],
                   "count": len(spots),
                   "app_type": 'food',
                   "campus_locations": CAMPUS_LOCATIONS}
        return context


class FoodDetailView(TemplateView):
    template_name = "404.html"

    @validate_campus_selection
    def get_context_data(self, **kwargs):
        self.template_name = kwargs['template_name']
        spot = get_spot_by_id(kwargs['spot_id'])
        spot = validate_detail_info(spot, kwargs['campus'], "food")
        if not spot:
            self.response_class = Response404
            self.template_name = "404.html"
            return custom_404_context(kwargs["campus"])

        context = {"spot": spot,
                   "campus": kwargs['campus'],
                   "app_type": 'food',
                   "campus_locations": CAMPUS_LOCATIONS}
        return context


class FoodFilterView(TemplateView):
    template_name = "404.html"

    @validate_campus_selection
    def get_context_data(self, **kwargs):
        self.template_name = kwargs['template_name']
        context = {"campus": kwargs['campus'],
                   "app_type": 'food',
                   "campus_locations": CAMPUS_LOCATIONS}
        return context


# study
class StudyListView(TemplateView):
    template_name = "404.html"

    @validate_campus_selection
    def get_context_data(self, **kwargs):
        self.template_name = kwargs['template_name']
        spots = get_filtered_spots(self.request, kwargs['campus'], "study")
        grouped_spots = group_spots_by_building(spots)
        context = {"spots": spots,
                   "campus": kwargs['campus'],
                   "grouped_spots": grouped_spots,
                   "count": len(spots),
                   "app_type": 'study',
                   "campus_locations": CAMPUS_LOCATIONS}
        return context


class StudyDetailView(TemplateView):
    template_name = "404.html"

    @validate_campus_selection
    def get_context_data(self, **kwargs):
        self.template_name = kwargs['template_name']
        spot = get_spot_by_id(kwargs['spot_id'])
        spot = validate_detail_info(spot, kwargs['campus'], "study")
        if not spot:
            self.response_class = Response404
            self.template_name = "404.html"
            return custom_404_context(kwargs["campus"])

        context = {"spot": spot,
                   "campus": kwargs['campus'],
                   "app_type": 'study',
                   "campus_locations": CAMPUS_LOCATIONS}
        return context


@ensure_csrf_cookie
def occupy_spot(request, campus, spot_id):
    spot = get_spot_by_id(spot_id)
    if not spot:
        request.response_class = Response404
        request.template_name = "404.html"
        return custom_404_context(campus)

    minutes = request.POST.get('minutes')
    students = request.POST.get('students')
    response = None
    if minutes != None and students != None:
        response = post_occupancy(spot_id, {'minutes': minutes, 'students': students})
        spot = get_spot_by_id(spot_id)

    if response != None and response.status == 403:
        error_message = "There is not enough room for %s more students" % students
        return render(request, 'scout/include/occupy.html', {'spot': spot, 'students': students, 'error': error_message})
    elif request.is_ajax():
        return render(request, 'scout/include/occupy.html', {'spot': spot, 'students': students})
    else:
        return redirect('study_detail', campus=campus, spot_id=spot_id)


class StudyFilterView(TemplateView):
    template_name = "404.html"

    @validate_campus_selection
    def get_context_data(self, **kwargs):
        self.template_name = kwargs['template_name']
        context = {"campus": kwargs['campus'],
                   "buildings": get_building_list(kwargs['campus']),
                   "app_type": 'study',
                   "campus_locations": CAMPUS_LOCATIONS}
        return context


# tech
class TechListView(TemplateView):
    template_name = "404.html"

    @validate_campus_selection
    def get_context_data(self, **kwargs):
        self.template_name = kwargs['template_name']
        # spots = get_spots_by_filter([('has_items', 'true')])
        self.request.GET = self.request.GET.copy()
        self.request.GET['item_is_active'] = 'true'
        spots = get_filtered_spots(self.request, kwargs['campus'], "tech")
        spots = get_filtered_items(spots, self.request)
        count = get_item_count(spots)
        if count <= 0:
            spots = []

        context = {"spots": spots,
                   "campus": kwargs['campus'],
                   "count": count,
                   "app_type": 'tech',
                   "campus_locations": CAMPUS_LOCATIONS}
        return context


class TechDetailView(TemplateView):
    template_name = "404.html"

    @validate_campus_selection
    def get_context_data(self, **kwargs):
        self.template_name = kwargs['template_name']
        spot = get_item_by_id(int(kwargs['item_id']))
        spot = validate_detail_info(spot, kwargs['campus'], "tech")
        if not spot:
            self.response_class = Response404
            self.template_name = "404.html"
            return custom_404_context(kwargs["campus"])

        context = {"spot": spot,
                   "campus": kwargs['campus'],
                   "app_type": 'tech',
                   "campus_locations": CAMPUS_LOCATIONS}
        return context


class TechFilterView(TemplateView):
    template_name = "404.html"

    @validate_campus_selection
    def get_context_data(self, **kwargs):
        self.template_name = kwargs['template_name']
        context = {"campus": kwargs['campus'],
                   "app_type": 'tech',
                   "campus_locations": CAMPUS_LOCATIONS}
        return context


def hybrid_comps_view(request):
    return render_to_response('hybridize/components.html',
                              context_instance=RequestContext(request))


# image views
def spot_image_view(request, image_id, spot_id):
    width = request.GET.get('width', None)
    try:
        resp, content = get_spot_image(spot_id, image_id, width)
        etag = resp.get('etag', None)
        response = HttpResponse(content, content_type=resp['content-type'])
        response['etag'] = etag
        return response
    except Exception:
        raise Http404


def item_image_view(request, image_id, item_id):
    width = request.GET.get('width', None)
    try:
        resp, content = get_item_image(item_id, image_id, width)
        etag = resp.get('etag', None)
        response = HttpResponse(content, content_type=resp['content-type'])
        response['etag'] = etag
        return response
    except Exception:
        raise Http404


# Custom method-based 404 page
def custom_404_response(request, campus=CAMPUS_LOCATIONS.keys()[0]):
    context = custom_404_context(campus)
    response = render_to_response('404.html', context,
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response


def custom_404_context(campus=CAMPUS_LOCATIONS.keys()[0]):
    context = {"campus": campus,
               "campus_locations": CAMPUS_LOCATIONS}
    return context


class Response404(TemplateResponse):
    status_code = 404
