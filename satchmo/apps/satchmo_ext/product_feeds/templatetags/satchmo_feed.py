from django import template
import re
try:
    from django.utils.safestring import mark_safe
except ImportError:
    mark_safe = lambda s:s

register = template.Library()

def rfc3339_date(date):
    return date.strftime('%Y-%m-%dT%H:%M:%SZ')

register.filter('atom_date', rfc3339_date)

def atom_tag_uri(url, date=None):
    tag = re.sub('^https?://', '', url)
            
    if date:
        tag = re.sub('/', ',%s:/' % date.strftime('%Y-%m-%d'), tag, 1)
        
    tag = re.sub('#', '/', tag)
    return 'tag:' + tag
    
register.filter('atom_tag_uri', atom_tag_uri)

def feed_safe_name(name):
    return name.replace(' ', '_').lower()

register.filter('feed_safe_name', feed_safe_name)

GOOGLE_TAGS = ('actor', 'age', 'age_range', 'agent', 'area', 'artist', 'aspect_ratio', 
    'author', 'bathrooms', 'battery_life', 'bedrooms', 'binding', 'brand', 'broker', 
    'calories', 'capacity', 'cholesterol', 'color', 'color_output', 'condition', 
    'cooking_time', 'course', 'course_date_range', 'course_number', 'course_times', 
    'cuisine', 'currency', 'department', 'description', 'director', 'display_type', 
    'edition', 'education', 'employer', 'ethnicity', 'event_date_range', 'event_type', 
    'expiration_date', 'expiration_date_time', 'feature', 'fiber', 'film_type', 'focus_type', 
    'format', 'from_location', 'functions', 'gender', 'genre', 'heel_height', 'height', 
    'hoa_dues', 'id', 'image_link', 'immigration_status', 'installation', 'interested_in', 
    'isbn', 'job_function', 'job_industry', 'job_type', 'language', 'length', 'link', 
    'listing_status', 'listing_type', 'load_type', 'location', 'lot_size', 'made_in', 
    'main_ingredient', 'make', 'marital_status', 'material', 'meal_type', 'megapixels', 
    'memory_card_slot', 'mileage', 'mls_listing_id', 'mls_name', 'model', 'model_number', 
    'mpn', 'name_of_item_reviewed', 'news_source', 'occasion', 'occupation', 'open_house_date_range', 
    'operating_system', 'optical_drive', 'pages', 'payment_accepted', 'payment_notes', 'performer', 
    'pickup', 'platform', 'preparation_time', 'price', 'price_type', 'processor_speed', 'product_type', 
    'property_taxes', 'property_type', 'protein', 'provider_class', 'provider_name', 
    'provider_telephone_number', 'publication_name', 'publication_volume', 'publish_date', 
    'publisher', 'quantity', 'rating', 'recommended_usage', 'resolution', 'review_type', 
    'reviewer_type', 'salary', 'salary_type', 'saturated_fat', 'school', 'school_district', 
    'screen_size', 'service_type', 'servings', 'sexual_orientation', 'shipping', 'shoe_width', 
    'size', 'sleeps', 'sodium', 'style', 'subject', 'tax_percent', 'tax_region', 'tech_spec_link', 
    'title', 'to_location', 'total_carbs', 'total_fat', 'travel_date_range', 'university', 'upc', 
    'url_of_item_reviewed', 'vehicle_type', 'venue_description', 'venue_name', 'venue_type', 
    'venue_website', 'vin', 'weight', 'width', 'wireless_interface', 'year', 'zoning', 'zoom'
)   
 
def make_googlebase_option(opt, custom):
    """Convert an option into a tag.  First look to see if it is a predefined tag, 
    if it is, good, use it.  Otherwise make a custom tag."""
    
    custom = custom.lower() in ('true','t','1')
    return make_googlebase_tag(opt.option_group.name, opt.name,custom)

register.filter('make_googlebase_option', make_googlebase_option)

def make_googlebase_attribute(att, custom):
    """Convert an attribute into a tag.  First look to see if it is a predefined tag, 
       if it is, good, use it.  Otherwise make a custom tag."""
     
    custom = custom.lower() in ('true','t','1')
    return make_googlebase_tag(att.name, att.value, custom)

register.filter('make_googlebase_attribute', make_googlebase_attribute)

def make_googlebase_tag(key, val, custom):
    """Convert a key/val pair into a tag.  First look to see if it is a predefined tag, 
    if it is, good, use it.  Otherwise make a custom tag."""
    key = feed_safe_name(key)
    
    if key in GOOGLE_TAGS:
        tag = "<g:%s>%s</g:%s>"
    elif key.endswith('s') and key[:-1] in GOOGLE_TAGS:
        key = key[:-1]
        tag = "<g:%s>%s</g:%s>"
    elif custom:
        tag = "<c:%s:string>%s</c:%s:string>"
    else:
        tag = None
    
    if tag:
        return mark_safe(tag % (key, val, key))
    else:
        return ""
    
def stripspaces(s):
    s = re.sub(r'^\s+', '', s)
    s = re.sub(r'\s+$', '', s)
    s = s.replace('\n\n','\n')
    return s
        
register.filter('stripspaces', stripspaces)