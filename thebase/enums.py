THEBASE_ENDPOINT = 'https://api.thebase.in/'
ITEMS_PER_PAGE = 10

GRANT_TYPE_AUTHORIZATION_CODE = 'authorization_code'
GRANT_TYPE_REFRESH_TOKEN = 'refresh_token'

TIMING_VALIDATION = 'validation'
TIMING_RUNTIME = 'runtime'

class ItemCols(object):
    COLUMN_COUNT = 91

    item_id = 0
    identifier = 1
    category_id = 2
    title = 3
    price = 4
    item_tax_type = 5
    detail = 6
    variation_start = 7
    stock = 47
    list_order = 48
    visible = 49
    delivery_company_id = 50
    img_origin_start = 51
    variation_stock_start = 71

