from dataclasses import dataclass


@dataclass
class AvitoSite:
    name: str = "avito.ru"
    start_url: str = "https://www.avito.ru/dagestan?forceLocation=1"
    # locations: str = "https://www.avito.ru/js/locations?json=true&id=646710"
    locations: str = (
        "https://www.avito.ru/web/1/slocations?locationId=646710&limit=100&q=%D0%A0%D0%B5%D1%81%D0%BF%D1%83%D0%B1%D0%BB%D0%B8%D0%BA%D0%B0%20%D0%94%D0%B0%D0%B3%D0%B5%D1%81%D1%82%D0%B0%D0%BD%20"
    )


@dataclass
class AvitoXpaths:
    to_ad: str = r"//a[contains(@data-marker,'item-title')]"
    to_name: str = r"//h1/span[@itemprop ='name']"
    to_address: str = r"//div[@itemprop ='address']"

    to_price_value: str = r"//div//span[@itemprop ='price']"
    to_price_currency: str = r"//div//span[@itemprop ='priceCurrency']"
    to_price_original: str = r"//div//span[contains(@class, 'price-value-string')]"

    to_square: str = r".*(площадь:.*?)\|"
    to_square_alter: str = r"площадь.*:.*\|"
    to_square_house: str = r"(площадь дома:.*?)\|"
    # to_square_flat: str = r"(Общая площадь:.*?)\|"

    to_list_ads: str = r"//div[contains(@elementtiming, 'bx.catalog.container')]"

    # "to_square":	"//div[@class ='item-params']//span[contains(text(),'Площадь') or contains(text(),'площадь')]/parent::li",
    # "to_square_alter":	"//div[@class ='item-params']//span[contains(text(),'Площадь') or contains(text(),'площадь')]/parent::span",
    # "to_square_house":	"//div[@class ='item-params']//span[contains(text(),'Площадь дома')]/parent::li",
    # "to_square_flat":	"//div[@class ='item-params']//span[contains(text(),'Общая площадь')]/parent::li",

    to_coord: str = r"//*[@data-map-lat]"
    # to_x: str = r"//div[contains(@class,'b-search-map')]"
    # to_y: str = r"//div[contains(@class,'b-search-map')]"

    to_description: str = r"//div[@itemprop ='description']"

    to_other1: str = r"//div[contains(@data-marker, 'item-params')]"
    to_other2: str = r"//span[contains(@class, 'breadcrumbs-link')]"

    # "to_next_page":		"//a[contains(@class,'pagination-next')]/@href",
    # "to_nedvizh":			"//a[contains(@class, 'category-with-counters-link') and contains(text(),'Недвижимость')]/@href",
    # "to_categories": "//a[(contains(@title, 'Квартиры'))]",

    to_nedvizh: str = (
        r"//a[(contains(@class, 'rubricator-list-') or contains(@class, 'js-catalog-counts__link')) and (contains(@title, 'Недвижимость'))]"
    )
    to_categories: str = r".//ul[not(li)]/parent::*/div/a"

    # "to_categories": "//a[(contains(@class, 'rubricator-link-') or contains(@class, 'js-catalog-counts__link')) and (contains(@title, 'Земельные участки') or contains(@title, 'Дома') or contains(@title, 'Гаражи') or contains(@title, 'Коммерческая'))]",
    # "to_categories": "//a[(contains(@title, 'Земельные участки') or contains(@title, 'Квартиры') or contains(@title, 'Дома') or contains(@title, 'Гаражи') or contains(@title, 'Коммерческая')) and (contains(@class, 'rubricator-link-') or contains(@class, 'js-catalog-counts__link'))]/@href",

    to_category: str = (
        r"//a[(contains(@class, 'rubricator-list-') or contains(@class, 'js-catalog-counts__link')) and (contains(@title, 'Недвижимость'))]//parent::div//parent::li/ul/li"
    )

    # "to_category":	  "//div[contains(@class,'breadcrumbs')]//span[(contains(text(), 'Недвижимость'))]//..//..//following-sibling::span[2]//span[1]/text()",
    # "to_category":	  "//div[contains(@class,'breadcrumbs')]/a[(contains(text(), 'Недвижимость'))]//following-sibling::a[1]/text()",

    # "to_sub_categories":	"//a[(contains(@title, 'Продам')) and (contains(@class, 'js-catalog-counts__link'))]/@href",

    to_date: str = r"//span[contains(@data-marker,'item-view/item-date')]"
    to_id: str = r"//head"

    to_search_form = r"//input[contains(@class,'input-input-')]"
    to_search_button = r"//button[contains(@data-marker,'search-form/submit-button')]"

    to_buy_button: str = (
        r"//div[contains(@class, 'radio-group-root_layout-horizontal')]//span[contains(text(), 'Купить')]"
    )
    to_view_all_button: str = (
        r"//button[contains(@data-marker, 'search-filters/submit-button')]"
    )
    to_next_button: str = (
        r"//span[contains(@data-marker,'pagination-button/next') and not(contains(@class, 'pagination-item_readonly'))]"
    )
