{
    "name"          : "Stock Report",
    "version"       : "1.0",
    "author"        : "Miftahussalam",
    "website"       : "https://miftahussalam.com",
    "category"      : "Reporting",
    "license"       : "LGPL-3",
    "support"       : "me@miftahussalam.com",
    "summary"       : "Stock Report",
    "description"   : """
        Stock Report

Goto :
- Settings >> Technical >> Reports >> Generic Excel Report
- Inventory > Reports > Generic Excel Report
    """,
    "depends"       : [
        "product",
        "stock",
        # "ms_generic_excel_report",
    ],
    "data"          : [
        "wizard/ms_generic_excel_report_wizard.xml",
        "data/ms.generic.excel.report.csv",
        "data/ms.generic.excel.report.line.csv",
    ],
    "demo"          : [],
    "test"          : [],
    "images"        : [
        "static/description/images/main_screenshot.png",
    ],
    "qweb"          : [],
    "css"           : [],
    "application"   : True,
    "installable"   : True,
    "auto_install"  : False,
}