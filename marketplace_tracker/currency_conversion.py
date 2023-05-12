import requests
import json
import re
import error_logger

def currency_string_conversion(start_currency, end_currency, currency_string, marketplace):
    currency_name = parse_currency_name(currency_string, marketplace)
    if currency_name == "":
        return currency_string
    if start_currency == "":
        start_currency = currency_name
    
    start_currency_value = parse_currency_value(currency_string, marketplace)
    if start_currency_value == "":
        return currency_string

    return convert_currency(start_currency, end_currency, start_currency_value)

def refresh_currency_conversions():
    currency_names = requests.get("https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies.min.json")
    currency_ratios = requests.get("https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/usd.min.json")

    if currency_names.status_code == 200:
        with open("currencies.min.json", "w", encoding = "utf8") as currency_names_file:
            currency_names_file.write(currency_names.text)
    else:
        error_logger.error_log("Currency names bad status code: " + str(currency_names.status_code) + ", Response headers: " + str(currency_names.headers) + ", Request response: " + str(currency_names.text), "")

    if currency_ratios.status_code == 200:
        with open("usd.min.json", "w", encoding = "utf8") as currency_ratios_file:
            currency_ratios_file.write(currency_ratios.text)
    else:
        error_logger.error_log("Currency ratios bad status code: " + str(currency_ratios.status_code) + ", Response headers: " + str(currency_ratios.headers) + ", Request response: " + str(currency_ratios.text), "")

def convert_currency(start_currency, end_currency, start_currency_value):
    currency_names_dict = {}
    with open("currencies.min.json", "r") as currency_names_file:
        currency_names_dict = json.load(currency_names_file)

    currency_ratios_dict = {}
    with open("usd.min.json", "r") as currency_ratios_file:
        currency_ratios_dict = json.load(currency_ratios_file)

    if start_currency.lower() not in currency_names_dict or end_currency.lower() not in currency_names_dict:
        error_logger.error_log("Bad currency names cannot convert currency from " + str(start_currency) + " to " + str(end_currency), "")
        return

    currency_ratio = currency_ratios_dict["usd"][end_currency] / currency_ratios_dict["usd"][start_currency]

    return start_currency_value * currency_ratio

def parse_currency_name(currency_string, marketplace):
    if marketplace == "blocket":
        return "sek"
    elif marketplace == "ebay":
        #special handling for currencies that ebay shows in odd ways
        if "c $" in currency_string.lower():
            return "cad"
        elif "au $" in currency_string.lower():
            return "aud"
        elif "us $" in currency_string.lower():
            return "usd"
        elif "$" in currency_string.lower(): #usd must be last due to other currencies that use the $ symbol
            return "usd"
        else:
            currency_names_dict = {}
            with open("currencies.min.json", "r") as currency_names_file:
                currency_names_dict = json.loads(currency_names_file)

            for key in sorted(list(currency_names_dict.keys()), key = len).reverse(): #currencies with longest abbreviations must be checked first
                if key in currency_string.lower():
                    return key

        error_logger.error_log("Parse currency bad ebay currency. Currency string: " + str(currency_string), "")
        return ""
    elif marketplace == "mercari_jp":
        return "jpy"
    elif marketplace == "mercari_us":
        return "usd"
    elif marketplace == "rakuma":
        return "jpy"
    elif marketplace == "tradera":
        return "sek"
    elif marketplace == "yahoo_auctions":
        return "jpy"
    else:
        error_logger.error_log("Parse currency bad marketplace name: " + str(marketplace) + ", Currency string: " + str(currency_string), "")
        return ""

def parse_currency_value(currency_string, marketplace):
    try:
        currency_value = re.sub("(\s|,)", "", re.findall("\d+(\s|,|\.|\d)*\d+", currency_string)[0])
    except Exception as e:
        error_logger.error_log("Currency value parsing failed. Currency string: " + str(currency_string), ", Marketplace: " + str(marketplace), e)
        return ""

    try:
        return int(currency_value)
    except Exception:
        pass
    try:
        return float(currency_value)
    except Exception:
        pass

    error_logger.error_log("Currency value to number failed. Currency value: " + str(currency_value) + ", Currency string: " + str(currency_string), ", Marketplace: " + str(marketplace), e)
    return ""
