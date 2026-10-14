import os
import uuid

def uid():
    return str(uuid.uuid4())

base_dir = r"f:\MAVEN DATA\Maven+Fuzzy+Factory\Maven Fuzzy Factory.SemanticModel\definition"
tables_dir = os.path.join(base_dir, "tables")
os.makedirs(tables_dir, exist_ok=True)

def col(name, data_type, is_source=True, source_col=None, is_inferred=False, format_str=None, dax_calc=None):
    quoted_name = f"'{name}'" if (" " in name or "%" in name or "$" in name or "-" in name) else name
    lines = []
    if dax_calc:
        lines.append(f"\tcolumn {quoted_name} = {dax_calc}")
    else:
        lines.append(f"\tcolumn {quoted_name}")
    lines.append(f"\t\tdataType: {data_type}")
    if format_str:
        lines.append(f"\t\tformatString: {format_str}")
    lines.append(f"\t\tlineageTag: {uid()}")
    lines.append(f"\t\tsummarizeBy: none")
    if is_inferred:
        lines.append(f"\t\tisNameInferred")
        sc = source_col or name
        lines.append(f"\t\tsourceColumn: [{sc}]")
    elif is_source and not dax_calc:
        sc = source_col or name
        lines.append(f"\t\tsourceColumn: {sc}")
    lines.append("")
    return "\n".join(lines)

# 1. products
products_cols = [
    col("product_id", "int64", is_source=True, format_str="0"),
    col("created_at", "dateTime", is_source=True, format_str="General Date"),
    col("product_name", "string", is_source=True),
    col("Retail Price", "double", dax_calc="SWITCH([product_id], 1, 49.99, 2, 59.99, 3, 45.99, 4, 29.99)", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("Unit COGS", "double", dax_calc="SWITCH([product_id], 1, 19.49, 2, 22.49, 3, 14.49, 4, 9.49)", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("Margin $", "double", dax_calc="[Retail Price] - [Unit COGS]", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("Margin %", "double", dax_calc="DIVIDE([Margin $], [Retail Price], 0)", format_str="0.00%"),
    col("Product Role", "string", dax_calc='SWITCH([product_id], 1, "Flagship Launch Bear", 2, "Premium Valentine\'s", 3, "Birthday Gift", 4, "Cross-Sell Add-on")')
]

products_m = '''\tpartition products = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t  Source = Csv.Document(File.Contents("F:\\MAVEN DATA\\Maven+Fuzzy+Factory\\products.csv"), [Delimiter = ",", Columns = 3, QuoteStyle = QuoteStyle.None]),
\t\t\t\t  #"Promoted headers" = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
\t\t\t\t  #"Changed column type" = Table.TransformColumnTypes(#"Promoted headers", {{"product_id", Int64.Type}, {"created_at", type datetime}, {"product_name", type text}})
\t\t\t\tin
\t\t\t\t  #"Changed column type"

\tannotation PBI_ResultType = Table
'''
products_tmdl = f"table products\n\tlineageTag: {uid()}\n\n" + "\n".join(products_cols) + "\n" + products_m

# 2. orders
orders_cols = [
    col("order_id", "int64", is_source=True, format_str="0"),
    col("created_at", "dateTime", is_source=True, format_str="General Date"),
    col("website_session_id", "int64", is_source=True, format_str="0"),
    col("user_id", "int64", is_source=True, format_str="0"),
    col("primary_product_id", "int64", is_source=True, format_str="0"),
    col("items_purchased", "int64", is_source=True, format_str="0"),
    col("price_usd", "double", is_source=True, format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("cogs_usd", "double", is_source=True, format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("Order Date", "dateTime", dax_calc="DATEVALUE([created_at])", format_str="yyyy-MM-dd"),
    col("Basket Type", "string", dax_calc='IF([items_purchased] = 1, "Single", "Bundle")'),
    col("Margin $", "double", dax_calc="[price_usd] - [cogs_usd]", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("Margin %", "double", dax_calc="DIVIDE([Margin $], [price_usd], 0)", format_str="0.00%"),
    col("Order Sequence", "int64", dax_calc="CALCULATE(COUNTROWS(orders), ALLEXCEPT(orders, orders[user_id]), orders[created_at] <= EARLIER(orders[created_at]))", format_str="0"),
    col("Is Repeat Order", "int64", dax_calc="IF([Order Sequence] > 1, 1, 0)", format_str="0"),
    col("Days Session to Order", "int64", dax_calc="DATEDIFF(LOOKUPVALUE(website_sessions[created_at], website_sessions[website_session_id], [website_session_id]), [created_at], DAY)", format_str="0")
]

orders_m = '''\tpartition orders = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t  Source = Csv.Document(File.Contents("F:\\MAVEN DATA\\Maven+Fuzzy+Factory\\orders.csv"), [Delimiter = ",", Columns = 8, QuoteStyle = QuoteStyle.None]),
\t\t\t\t  #"Promoted headers" = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
\t\t\t\t  #"Changed column type" = Table.TransformColumnTypes(#"Promoted headers", {{"order_id", Int64.Type}, {"created_at", type datetime}, {"website_session_id", Int64.Type}, {"user_id", Int64.Type}, {"primary_product_id", Int64.Type}, {"items_purchased", Int64.Type}, {"price_usd", type number}, {"cogs_usd", type number}})
\t\t\t\tin
\t\t\t\t  #"Changed column type"

\tannotation PBI_ResultType = Table
'''
orders_tmdl = f"table orders\n\tlineageTag: {uid()}\n\n" + "\n".join(orders_cols) + "\n" + orders_m

# 3. order_items
order_items_cols = [
    col("order_item_id", "int64", is_source=True, format_str="0"),
    col("created_at", "dateTime", is_source=True, format_str="General Date"),
    col("order_id", "int64", is_source=True, format_str="0"),
    col("product_id", "int64", is_source=True, format_str="0"),
    col("is_primary_item", "int64", is_source=True, format_str="0"),
    col("price_usd", "double", is_source=True, format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("cogs_usd", "double", is_source=True, format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("Order Date", "dateTime", dax_calc="DATEVALUE([created_at])", format_str="yyyy-MM-dd"),
    col("Item Role", "string", dax_calc='IF([is_primary_item] = 1, "Primary Item", "Cross-Sell Item")'),
    col("Margin $", "double", dax_calc="[price_usd] - [cogs_usd]", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("Margin %", "double", dax_calc="DIVIDE([Margin $], [price_usd], 0)", format_str="0.00%"),
    col("Refund Amount", "double", dax_calc="LOOKUPVALUE(order_item_refunds[refund_amount_usd], order_item_refunds[order_item_id], [order_item_id], 0)", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("Is Refunded", "int64", dax_calc="IF([Refund Amount] > 0, 1, 0)", format_str="0")
]

order_items_m = '''\tpartition order_items = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t  Source = Csv.Document(File.Contents("F:\\MAVEN DATA\\Maven+Fuzzy+Factory\\order_items.csv"), [Delimiter = ",", Columns = 7, QuoteStyle = QuoteStyle.None]),
\t\t\t\t  #"Promoted headers" = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
\t\t\t\t  #"Changed column type" = Table.TransformColumnTypes(#"Promoted headers", {{"order_item_id", Int64.Type}, {"created_at", type datetime}, {"order_id", Int64.Type}, {"product_id", Int64.Type}, {"is_primary_item", Int64.Type}, {"price_usd", type number}, {"cogs_usd", type number}})
\t\t\t\tin
\t\t\t\t  #"Changed column type"

\tannotation PBI_ResultType = Table
'''
order_items_tmdl = f"table order_items\n\tlineageTag: {uid()}\n\n" + "\n".join(order_items_cols) + "\n" + order_items_m

refunds_created_at = '''\tcolumn created_at
\t\tdataType: dateTime
\t\tformatString: General Date
\t\tlineageTag: 89ca3c86-7625-4375-8dda-e1a3fe2431ce
\t\tsummarizeBy: none
\t\tsourceColumn: created_at

\t\tvariation Variation
\t\t\tisDefault
\t\t\trelationship: 780db2d4-117d-491d-a3de-5f36d98d6a5d
\t\t\tdefaultHierarchy: LocalDateTable_1580720a-eb97-4948-bb47-5b731dcf40a7.'Date Hierarchy'

\t\tannotation SummarizationSetBy = Automatic
'''

refunds_cols = [
    col("order_item_refund_id", "int64", is_source=True, format_str="0"),
    refunds_created_at,
    col("order_item_id", "int64", is_source=True, format_str="0"),
    col("order_id", "int64", is_source=True, format_str="0"),
    col("refund_amount_usd", "double", is_source=True, format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("Refund Date", "dateTime", dax_calc="DATEVALUE([created_at])", format_str="yyyy-MM-dd"),
    col("Order Date", "dateTime", dax_calc="LOOKUPVALUE(orders[Order Date], orders[order_id], [order_id])", format_str="yyyy-MM-dd"),
    col("Lag Days", "int64", dax_calc="DATEDIFF(LOOKUPVALUE(orders[created_at], orders[order_id], [order_id]), [created_at], DAY)", format_str="0"),
    col("Lag Bucket", "string", dax_calc='SWITCH(TRUE(), [Lag Days] <= 5, "2-5 Days", [Lag Days] <= 10, "6-10 Days", "11-16 Days")')
]

refunds_m = '''\tpartition order_item_refunds = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t  Source = Csv.Document(File.Contents("F:\\MAVEN DATA\\Maven+Fuzzy+Factory\\order_item_refunds.csv"), [Delimiter = ",", Columns = 5, QuoteStyle = QuoteStyle.None]),
\t\t\t\t  #"Promoted headers" = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
\t\t\t\t  #"Changed column type" = Table.TransformColumnTypes(#"Promoted headers", {{"order_item_refund_id", Int64.Type}, {"created_at", type datetime}, {"order_item_id", Int64.Type}, {"order_id", Int64.Type}, {"refund_amount_usd", type number}})
\t\t\t\tin
\t\t\t\t  #"Changed column type"

\tannotation PBI_ResultType = Table
'''
order_item_refunds_tmdl = f"table order_item_refunds\n\tlineageTag: {uid()}\n\n" + "\n".join(refunds_cols) + "\n" + refunds_m

# 5. website_sessions
sessions_cols = [
    col("website_session_id", "int64", is_source=True, format_str="0"),
    col("created_at", "dateTime", is_source=True, format_str="General Date"),
    col("user_id", "int64", is_source=True, format_str="0"),
    col("is_repeat_session", "int64", is_source=True, format_str="0"),
    col("utm_source", "string", is_source=True),
    col("utm_campaign", "string", is_source=True),
    col("utm_content", "string", is_source=True),
    col("device_type", "string", is_source=True),
    col("http_referer", "string", is_source=True),
    col("Session Date", "dateTime", dax_calc="DATEVALUE([created_at])", format_str="yyyy-MM-dd"),
    col("Channel Grouping", "string", dax_calc='SWITCH(TRUE(), ISBLANK([utm_source]) && ISBLANK([http_referer]), "Direct Type-In", ISBLANK([utm_source]) && NOT(ISBLANK([http_referer])), "Organic Search", [utm_source] = "gsearch" && [utm_campaign] = "brand", "Paid: Google Brand", [utm_source] = "gsearch" && [utm_campaign] = "nonbrand", "Paid: Google Nonbrand", [utm_source] = "bsearch" && [utm_campaign] = "brand", "Paid: Bing Brand", [utm_source] = "bsearch" && [utm_campaign] = "nonbrand", "Paid: Bing Nonbrand", [utm_source] = "socialbook", "Paid Social", "Other")'),
    col("Traffic Type", "string", dax_calc='IF(ISBLANK([utm_source]), IF(ISBLANK([http_referer]), "Direct", "Organic"), "Paid")'),
    col("Pageviews", "int64", dax_calc="COUNTROWS(RELATEDTABLE(website_pageviews))", format_str="0"),
    col("Is Bounce", "int64", dax_calc="IF([Pageviews] = 1, 1, 0)", format_str="0"),
    col("Landing Page", "string", dax_calc="CALCULATE(SELECTEDVALUE(website_pageviews[pageview_url]), TOPN(1, RELATEDTABLE(website_pageviews), website_pageviews[website_pageview_id], ASC))"),
    col("Reached Products", "int64", dax_calc='IF(CALCULATE(COUNTROWS(RELATEDTABLE(website_pageviews)), website_pageviews[pageview_url] = "/products") > 0, 1, 0)', format_str="0"),
    col("Reached Product Detail", "int64", dax_calc='IF(CALCULATE(COUNTROWS(RELATEDTABLE(website_pageviews)), website_pageviews[pageview_url] IN {"/the-original-mr-fuzzy", "/the-forever-love-bear", "/the-birthday-sugar-panda", "/the-hudson-river-mini-bear"}) > 0, 1, 0)', format_str="0"),
    col("Reached Cart", "int64", dax_calc='IF(CALCULATE(COUNTROWS(RELATEDTABLE(website_pageviews)), website_pageviews[pageview_url] = "/cart") > 0, 1, 0)', format_str="0"),
    col("Reached Shipping", "int64", dax_calc='IF(CALCULATE(COUNTROWS(RELATEDTABLE(website_pageviews)), website_pageviews[pageview_url] = "/shipping") > 0, 1, 0)', format_str="0"),
    col("Reached Billing", "int64", dax_calc='IF(CALCULATE(COUNTROWS(RELATEDTABLE(website_pageviews)), website_pageviews[pageview_url] = "/billing") > 0, 1, 0)', format_str="0"),
    col("Reached Billing2", "int64", dax_calc='IF(CALCULATE(COUNTROWS(RELATEDTABLE(website_pageviews)), website_pageviews[pageview_url] = "/billing-2") > 0, 1, 0)', format_str="0"),
    col("Reached ThankYou", "int64", dax_calc='IF(CALCULATE(COUNTROWS(RELATEDTABLE(website_pageviews)), website_pageviews[pageview_url] = "/thank-you-for-your-order") > 0, 1, 0)', format_str="0"),
    col("Billing Variant", "string", dax_calc='IF([Reached Billing2] = 1, "billing-2", IF([Reached Billing] = 1, "billing", "n/a"))'),
    col("Chapter ID", "int64", dax_calc="SWITCH(TRUE(), [created_at] >= DATE(2015, 1, 1), 5, [created_at] >= DATE(2014, 2, 1), 4, [created_at] >= DATE(2013, 1, 1), 3, [created_at] >= DATE(2012, 9, 1), 2, 1)", format_str="0")
]

sessions_m = '''\tpartition website_sessions = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t  Source = Csv.Document(File.Contents("F:\\MAVEN DATA\\Maven+Fuzzy+Factory\\website_sessions.csv"), [Delimiter = ",", Columns = 9, QuoteStyle = QuoteStyle.None]),
\t\t\t\t  #"Promoted headers" = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
\t\t\t\t  #"Changed column type" = Table.TransformColumnTypes(#"Promoted headers", {{"website_session_id", Int64.Type}, {"created_at", type datetime}, {"user_id", Int64.Type}, {"is_repeat_session", Int64.Type}, {"utm_source", type text}, {"utm_campaign", type text}, {"utm_content", type text}, {"device_type", type text}, {"http_referer", type text}}),
\t\t\t\t  #"Replaced NULLs" = Table.ReplaceValue(#"Changed column type", "NULL", null, Replacer.ReplaceValue, {"utm_source", "utm_campaign", "utm_content", "http_referer"})
\t\t\t\tin
\t\t\t\t  #"Replaced NULLs"

\tannotation PBI_ResultType = Table
'''
website_sessions_tmdl = f"table website_sessions\n\tlineageTag: {uid()}\n\n" + "\n".join(sessions_cols) + "\n" + sessions_m

# 6. website_pageviews
pv_cols = [
    col("website_pageview_id", "int64", is_source=True, format_str="0"),
    col("created_at", "dateTime", is_source=True, format_str="General Date"),
    col("website_session_id", "int64", is_source=True, format_str="0"),
    col("pageview_url", "string", is_source=True),
    col("Pageview Date", "dateTime", dax_calc="DATEVALUE([created_at])", format_str="yyyy-MM-dd"),
    col("Page Category", "string", dax_calc='SWITCH(TRUE(), [pageview_url] IN {"/home", "/lander-1", "/lander-2", "/lander-3", "/lander-4", "/lander-5"}, "Landing Page", [pageview_url] = "/products", "Catalog", [pageview_url] IN {"/the-original-mr-fuzzy", "/the-forever-love-bear", "/the-birthday-sugar-panda", "/the-hudson-river-mini-bear"}, "Product Detail", [pageview_url] IN {"/cart", "/shipping", "/billing", "/billing-2"}, "Checkout Funnel", [pageview_url] = "/thank-you-for-your-order", "Conversion", "Other")')
]

pv_m = '''\tpartition website_pageviews = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t  Source = Csv.Document(File.Contents("F:\\MAVEN DATA\\Maven+Fuzzy+Factory\\website_pageviews.csv"), [Delimiter = ",", Columns = 4, QuoteStyle = QuoteStyle.None]),
\t\t\t\t  #"Promoted headers" = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
\t\t\t\t  #"Changed column type" = Table.TransformColumnTypes(#"Promoted headers", {{"website_pageview_id", Int64.Type}, {"created_at", type datetime}, {"website_session_id", Int64.Type}, {"pageview_url", type text}})
\t\t\t\tin
\t\t\t\t  #"Changed column type"

\tannotation PBI_ResultType = Table
'''
website_pageviews_tmdl = f"table website_pageviews\n\tlineageTag: {uid()}\n\n" + "\n".join(pv_cols) + "\n" + pv_m

# 7. Dim_Date
dim_date_cols = [
    col("Date", "dateTime", is_inferred=True, format_str="yyyy-MM-dd"),
    col("Year", "int64", is_inferred=True, format_str="0"),
    col("YearMonth", "string", is_inferred=True),
    col("MonthName", "string", is_inferred=True),
    col("MonthNumber", "int64", is_inferred=True, format_str="0"),
    col("MonthSort", "int64", is_inferred=True, format_str="0"),
    col("Quarter", "string", is_inferred=True),
    col("YearQuarter", "string", is_inferred=True),
    col("DayOfWeek", "string", is_inferred=True),
    col("DayOfWeekNumber", "int64", is_inferred=True, format_str="0"),
    col("IsWeekend", "string", is_inferred=True),
    col("WeekOfYear", "int64", is_inferred=True, format_str="0"),
    col("Chapter ID", "int64", is_inferred=True, format_str="0")
]
dim_date_part = '''\tpartition Dim_Date = calculated
\t\tmode: import
\t\tsource = ADDCOLUMNS(CALENDAR(DATE(2012, 1, 1), DATE(2015, 12, 31)), "Year", YEAR([Date]), "YearMonth", FORMAT([Date], "yyyy-MM"), "MonthName", FORMAT([Date], "mmm"), "MonthNumber", MONTH([Date]), "MonthSort", YEAR([Date]) * 100 + MONTH([Date]), "Quarter", "Q" & QUARTER([Date]), "YearQuarter", YEAR([Date]) & " Q" & QUARTER([Date]), "DayOfWeek", FORMAT([Date], "ddd"), "DayOfWeekNumber", WEEKDAY([Date], 2), "IsWeekend", IF(WEEKDAY([Date], 2) >= 6, "Weekend", "Weekday"), "WeekOfYear", WEEKNUM([Date], 2), "Chapter ID", SWITCH(TRUE(), [Date] >= DATE(2015, 1, 1), 5, [Date] >= DATE(2014, 2, 1), 4, [Date] >= DATE(2013, 1, 1), 3, [Date] >= DATE(2012, 9, 1), 2, 1))

\tannotation PBI_Id = ''' + uid() + "\n"
dim_date_tmdl = f"table Dim_Date\n\tlineageTag: {uid()}\n\tdataCategory: Time\n\n" + "\n".join(dim_date_cols) + "\n" + dim_date_part

# 8. Dim_Channel
dim_chan_cols = [
    col("Channel Grouping", "string", is_inferred=True),
    col("Traffic Type", "string", is_inferred=True),
    col("utm_source", "string", is_inferred=True),
    col("utm_campaign", "string", is_inferred=True)
]
dim_chan_part = '''\tpartition Dim_Channel = calculated
\t\tmode: import
\t\tsource = SUMMARIZE(website_sessions, website_sessions[Channel Grouping], website_sessions[Traffic Type], website_sessions[utm_source], website_sessions[utm_campaign])

\tannotation PBI_Id = ''' + uid() + "\n"
dim_channel_tmdl = f"table Dim_Channel\n\tlineageTag: {uid()}\n\n" + "\n".join(dim_chan_cols) + "\n" + dim_chan_part

# 9. Dim_Lander
dim_lander_cols = [
    col("Lander", "string", is_inferred=True),
    col("Launch", "dateTime", is_inferred=True, format_str="General Date"),
    col("Retired", "dateTime", is_inferred=True, format_str="General Date"),
    col("Lander Order", "int64", is_inferred=True, format_str="0")
]
dim_lander_part = '''\tpartition Dim_Lander = calculated
\t\tmode: import
\t\tsource = DATATABLE("Lander", STRING, "Launch", DATETIME, "Retired", DATETIME, "Lander Order", INTEGER, {{"/home", "2012-03-19T08:00:00", "2015-03-19T23:59:59", 1}, {"/lander-1", "2012-06-19T00:00:00", "2013-03-10T23:59:59", 2}, {"/lander-2", "2013-01-14T00:00:00", "2014-12-27T23:59:59", 3}, {"/lander-3", "2013-07-09T00:00:00", "2015-03-19T23:59:59", 4}, {"/lander-4", "2014-02-02T00:00:00", "2014-04-19T23:59:59", 5}, {"/lander-5", "2014-08-02T00:00:00", "2015-03-19T23:59:59", 6}})

\tannotation PBI_Id = ''' + uid() + "\n"
dim_lander_tmdl = f"table Dim_Lander\n\tlineageTag: {uid()}\n\n" + "\n".join(dim_lander_cols) + "\n" + dim_lander_part

# 10. Dim_Customer
dim_cust_cols = [
    col("user_id", "int64", is_inferred=True, format_str="0"),
    col("FirstVisit", "dateTime", is_inferred=True, format_str="General Date"),
    col("TotalVisits", "int64", is_inferred=True, format_str="0"),
    col("Cohort Month", "string", is_inferred=True),
    col("Cohort Quarter", "string", is_inferred=True),
    col("Is Repeater", "string", is_inferred=True)
]
dim_cust_part = '''\tpartition Dim_Customer = calculated
\t\tmode: import
\t\tsource = ADDCOLUMNS(SUMMARIZE(website_sessions, website_sessions[user_id], "FirstVisit", MIN(website_sessions[created_at]), "TotalVisits", COUNTROWS(website_sessions)), "Cohort Month", FORMAT([FirstVisit], "yyyy-MM"), "Cohort Quarter", YEAR([FirstVisit]) & " Q" & QUARTER([FirstVisit]), "Is Repeater", IF([TotalVisits] > 1, "Repeat Visitor", "One-Time Visitor"))

\tannotation PBI_Id = ''' + uid() + "\n"
dim_customer_tmdl = f"table Dim_Customer\n\tlineageTag: {uid()}\n\n" + "\n".join(dim_cust_cols) + "\n" + dim_cust_part

# 11. Basket_Pairs
bp_cols = [
    col("order_item_id", "int64", is_inferred=True, format_str="0"),
    col("created_at", "dateTime", is_inferred=True, format_str="General Date"),
    col("order_id", "int64", is_inferred=True, format_str="0"),
    col("product_id", "int64", is_inferred=True, format_str="0"),
    col("is_primary_item", "int64", is_inferred=True, format_str="0"),
    col("price_usd", "double", is_inferred=True, format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("cogs_usd", "double", is_inferred=True, format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("PrimaryProductID", "int64", is_inferred=True, format_str="0"),
    col("CrossProductID", "int64", is_inferred=True, format_str="0")
]
bp_part = '''\tpartition Basket_Pairs = calculated
\t\tmode: import
\t\tsource = ADDCOLUMNS(FILTER(order_items, order_items[is_primary_item] = 0), "PrimaryProductID", LOOKUPVALUE(orders[primary_product_id], orders[order_id], [order_id]), "CrossProductID", [product_id])
'''
basket_pairs_tmdl = f"table Basket_Pairs\n\tlineageTag: {uid()}\n\n" + "\n".join(bp_cols) + "\n" + bp_part

# 12. _Param_Metric
pm_cols = [
    col("MetricID", "int64", is_inferred=True, format_str="0"),
    col("MetricName", "string", is_inferred=True),
    col("Category", "string", is_inferred=True),
    col("FormatType", "string", is_inferred=True),
    col("SortOrder", "int64", is_inferred=True, format_str="0")
]
pm_part = '''\tpartition _Param_Metric = calculated
\t\tmode: import
\t\tsource = DATATABLE("MetricID", INTEGER, "MetricName", STRING, "Category", STRING, "FormatType", STRING, "SortOrder", INTEGER, {{1, "Gross Revenue", "Financial", "Currency", 1}, {2, "Net Revenue", "Financial", "Currency", 2}, {3, "Gross Profit", "Financial", "Currency", 3}, {4, "Gross Margin %", "Financial", "Percentage", 4}, {5, "Total Orders", "Volume", "Integer", 5}, {6, "Total Sessions", "Volume", "Integer", 6}, {7, "Conversion Rate %", "Efficiency", "Percentage", 7}, {8, "Average Order Value", "Basket", "Currency", 8}, {9, "Cross-Sell Attach %", "Basket", "Percentage", 9}, {10, "Refund Rate %", "Quality", "Percentage", 10}})

\tannotation PBI_Id = ''' + uid() + "\n"
param_metric_tmdl = f"table _Param_Metric\n\tlineageTag: {uid()}\n\n" + "\n".join(pm_cols) + "\n" + pm_part

# 13. _Param_Time
pt_cols = [
    col("TimeModeID", "int64", is_inferred=True, format_str="0"),
    col("TimeModeName", "string", is_inferred=True),
    col("Description", "string", is_inferred=True),
    col("SortOrder", "int64", is_inferred=True, format_str="0")
]
pt_part = '''\tpartition _Param_Time = calculated
\t\tmode: import
\t\tsource = DATATABLE("TimeModeID", INTEGER, "TimeModeName", STRING, "Description", STRING, "SortOrder", INTEGER, {{1, "Current Actuals", "Base period actuals", 1}, {2, "Previous Period (PoP)", "Comparison vs prior period", 2}, {3, "Previous Year (YoY)", "Comparison vs same period prior year", 3}, {4, "YoY Variance ($/Vol)", "Absolute difference vs prior year", 4}, {5, "YoY Variance %", "Percentage variance vs prior year", 5}, {6, "Rolling 30 Days", "30-day smoothed moving average", 6}})

\tannotation PBI_Id = ''' + uid() + "\n"
param_time_tmdl = f"table _Param_Time\n\tlineageTag: {uid()}\n\n" + "\n".join(pt_cols) + "\n" + pt_part

# 14. _Param_Dim
pd_cols = [
    col("DimensionID", "int64", is_inferred=True, format_str="0"),
    col("DimensionName", "string", is_inferred=True),
    col("SortOrder", "int64", is_inferred=True, format_str="0")
]
pd_part = '''\tpartition _Param_Dim = calculated
\t\tmode: import
\t\tsource = DATATABLE("DimensionID", INTEGER, "DimensionName", STRING, "SortOrder", INTEGER, {{1, "Channel Grouping", 1}, {2, "Device Type", 2}, {3, "Primary Product", 3}, {4, "Landing Page", 4}, {5, "Campaign", 5}})

\tannotation PBI_Id = ''' + uid() + "\n"
param_dim_tmdl = f"table _Param_Dim\n\tlineageTag: {uid()}\n\n" + "\n".join(pd_cols) + "\n" + pd_part

# 15. _Param_Story
ps_cols = [
    col("ChapterID", "int64", is_inferred=True, format_str="0"),
    col("ChapterName", "string", is_inferred=True),
    col("Timeframe", "string", is_inferred=True),
    col("Headline", "string", is_inferred=True),
    col("Commentary", "string", is_inferred=True),
    col("StartDate", "dateTime", is_inferred=True, format_str="General Date"),
    col("EndDate", "dateTime", is_inferred=True, format_str="General Date")
]
ps_part = '''\tpartition _Param_Story = calculated
\t\tmode: import
\t\tsource = DATATABLE("ChapterID", INTEGER, "ChapterName", STRING, "Timeframe", STRING, "Headline", STRING, "Commentary", STRING, "StartDate", DATETIME, "EndDate", DATETIME, {{1, "Ch1 Search Launch", "Mar 2012 – Aug 2012", "Bootstrapping on Google Paid Search", "Single product (Mr. Fuzzy), high desktop dependency, baseline conversion ~3.5%.", "2012-03-19T00:00:00", "2012-08-31T23:59:59"}, {2, "Ch2 Billing Breakthrough", "Sep 2012 – Dec 2012", "Fixing the Leaky Checkout Bucket", "Billing-2 A/B test launched, lifting checkout completion from 44.8% to 63.4%.", "2012-09-01T00:00:00", "2012-12-31T23:59:59"}, {3, "Ch3 Diversification", "Jan 2013 – Jan 2014", "Expanding Search & Introducing Love Bear", "Bing paid search launched, Love Bear added, conversion crossed 6.6%.", "2013-01-01T00:00:00", "2014-01-31T23:59:59"}, {4, "Ch4 Cross-Sell Revolution", "Feb 2014 – Dec 2014", "The Hudson Mini Bear Basket Multiplier", "Mini Bear launched as cross-sell add-on, lifting AOV from $50 to $60 and pushing revenue past $1M.", "2014-02-01T00:00:00", "2014-12-31T23:59:59"}, {5, "Ch5 Scaled Maturity", "Jan 2015 – Mar 2015", "The Omnichannel High-Conversion Machine", "Conversion peaks at 8.44%, organic/direct traffic compounds, $1.85M net revenue reached.", "2015-01-01T00:00:00", "2015-03-19T23:59:59"}})

\tannotation PBI_Id = ''' + uid() + "\n"
param_story_tmdl = f"table _Param_Story\n\tlineageTag: {uid()}\n\n" + "\n".join(ps_cols) + "\n" + ps_part

# 16. _Param_CVR_Lift
pcvr_cols = [col("Value", "double", is_inferred=True, format_str="0.00%")]
pcvr_part = '''\tpartition _Param_CVR_Lift = calculated
\t\tmode: import
\t\tsource = GENERATESERIES(-0.20, 0.50, 0.01)

\tannotation PBI_Id = ''' + uid() + "\n"
param_cvr_lift_tmdl = f"table _Param_CVR_Lift\n\tlineageTag: {uid()}\n\n" + "\n".join(pcvr_cols) + "\n" + pcvr_part

# 17. _Param_Refund_Cut
pref_cols = [col("Value", "double", is_inferred=True, format_str="0.00%")]
pref_part = '''\tpartition _Param_Refund_Cut = calculated
\t\tmode: import
\t\tsource = GENERATESERIES(-0.50, 0.00, 0.01)

\tannotation PBI_Id = ''' + uid() + "\n"
param_refund_cut_tmdl = f"table _Param_Refund_Cut\n\tlineageTag: {uid()}\n\n" + "\n".join(pref_cols) + "\n" + pref_part

# 18. _Param_Attach
patt_cols = [col("Value", "double", is_inferred=True, format_str="0.00%")]
patt_part = '''\tpartition _Param_Attach = calculated
\t\tmode: import
\t\tsource = GENERATESERIES(0.00, 0.40, 0.01)

\tannotation PBI_Id = ''' + uid() + "\n"
param_attach_tmdl = f"table _Param_Attach\n\tlineageTag: {uid()}\n\n" + "\n".join(patt_cols) + "\n" + patt_part

# 19. _Param_Target
ptar_cols = [
    col("TargetID", "int64", is_inferred=True, format_str="0"),
    col("TargetName", "string", is_inferred=True),
    col("TargetCVR", "double", is_inferred=True, format_str="0.00%"),
    col("TargetAOV", "double", is_inferred=True, format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00")
]
ptar_part = '''\tpartition _Param_Target = calculated
\t\tmode: import
\t\tsource = DATATABLE("TargetID", INTEGER, "TargetName", STRING, "TargetCVR", DOUBLE, "TargetAOV", DOUBLE, {{1, "Budget Target (7.5% CVR)", 0.075, 60.0}, {2, "Prior Year Benchmark", 0.066, 55.0}, {3, "DTC Industry Standard (5% CVR)", 0.050, 50.0}})

\tannotation PBI_Id = ''' + uid() + "\n"
param_target_tmdl = f"table _Param_Target\n\tlineageTag: {uid()}\n\n" + "\n".join(ptar_cols) + "\n" + ptar_part

# 20. _Param_LanderA
pla_cols = [
    col("LanderA", "string", is_inferred=True),
    col("SortOrder", "int64", is_inferred=True, format_str="0")
]
pla_part = '''\tpartition _Param_LanderA = calculated
\t\tmode: import
\t\tsource = DATATABLE("LanderA", STRING, "SortOrder", INTEGER, {{"/home", 1}, {"/lander-1", 2}, {"/lander-2", 3}, {"/lander-3", 4}, {"/lander-4", 5}, {"/lander-5", 6}})

\tannotation PBI_Id = ''' + uid() + "\n"
param_lander_a_tmdl = f"table _Param_LanderA\n\tlineageTag: {uid()}\n\n" + "\n".join(pla_cols) + "\n" + pla_part

# 21. _Param_LanderB
plb_cols = [
    col("LanderB", "string", is_inferred=True),
    col("SortOrder", "int64", is_inferred=True, format_str="0")
]
plb_part = '''\tpartition _Param_LanderB = calculated
\t\tmode: import
\t\tsource = DATATABLE("LanderB", STRING, "SortOrder", INTEGER, {{"/home", 1}, {"/lander-1", 2}, {"/lander-2", 3}, {"/lander-3", 4}, {"/lander-4", 5}, {"/lander-5", 6}})

\tannotation PBI_Id = ''' + uid() + "\n"
param_lander_b_tmdl = f"table _Param_LanderB\n\tlineageTag: {uid()}\n\n" + "\n".join(plb_cols) + "\n" + plb_part

# 22. _Param_CohortAge
pca_cols = [col("Value", "int64", is_inferred=True, format_str="0")]
pca_part = '''\tpartition _Param_CohortAge = calculated
\t\tmode: import
\t\tsource = GENERATESERIES(0, 12, 1)

\tannotation PBI_Id = ''' + uid() + "\n"
param_cohort_age_tmdl = f"table _Param_CohortAge\n\tlineageTag: {uid()}\n\n" + "\n".join(pca_cols) + "\n" + pca_part

# 23. _Dim_FunnelStep
dfs_cols = [
    col("StepNumber", "int64", is_inferred=True, format_str="0"),
    col("StepName", "string", is_inferred=True),
    col("PageURL", "string", is_inferred=True)
]
dfs_part = '''\tpartition _Dim_FunnelStep = calculated
\t\tmode: import
\t\tsource = DATATABLE("StepNumber", INTEGER, "StepName", STRING, "PageURL", STRING, {{1, "1. Entry Landing Page", "/lander"}, {2, "2. Browse Products", "/products"}, {3, "3. Product Detail View", "/detail"}, {4, "4. Add to Cart", "/cart"}, {5, "5. Shipping Details", "/shipping"}, {6, "6. Billing & Payment", "/billing"}, {7, "7. Purchase Confirmation", "/thank-you-for-your-order"}})

\tannotation PBI_Id = ''' + uid() + "\n"
dim_funnel_step_tmdl = f"table _Dim_FunnelStep\n\tlineageTag: {uid()}\n\n" + "\n".join(dfs_cols) + "\n" + dfs_part

# 24. _Measures
measures_body = f"""\tmeasure 'Total Sessions' = COUNTROWS(website_sessions)
\t\tformatString: #,0
\t\tlineageTag: {uid()}

\tmeasure 'Total Orders' = COUNTROWS(orders)
\t\tformatString: #,0
\t\tlineageTag: {uid()}

\tmeasure 'Gross Revenue' = SUM(order_items[price_usd])
\t\tformatString: \\$#,0.00;(\\$#,0.00);\\$#,0.00
\t\tlineageTag: {uid()}

\tmeasure 'Total COGS' = SUM(order_items[cogs_usd])
\t\tformatString: \\$#,0.00;(\\$#,0.00);\\$#,0.00
\t\tlineageTag: {uid()}

\tmeasure 'Gross Profit' = [Gross Revenue] - [Total COGS]
\t\tformatString: \\$#,0.00;(\\$#,0.00);\\$#,0.00
\t\tlineageTag: {uid()}

\tmeasure 'Gross Margin %' = DIVIDE([Gross Profit], [Gross Revenue], 0)
\t\tformatString: 0.00%
\t\tlineageTag: {uid()}

\tmeasure 'Total Refunds' = SUM(order_item_refunds[refund_amount_usd])
\t\tformatString: \\$#,0.00;(\\$#,0.00);\\$#,0.00
\t\tlineageTag: {uid()}

\tmeasure 'Net Revenue' = [Gross Revenue] - [Total Refunds]
\t\tformatString: \\$#,0.00;(\\$#,0.00);\\$#,0.00
\t\tlineageTag: {uid()}

\tmeasure 'Net Profit' = [Gross Profit] - [Total Refunds]
\t\tformatString: \\$#,0.00;(\\$#,0.00);\\$#,0.00
\t\tlineageTag: {uid()}

\tmeasure 'Net Margin %' = DIVIDE([Net Profit], [Net Revenue], 0)
\t\tformatString: 0.00%
\t\tlineageTag: {uid()}

\tmeasure 'Conversion Rate %' = DIVIDE([Total Orders], [Total Sessions], 0)
\t\tformatString: 0.00%
\t\tlineageTag: {uid()}

\tmeasure 'Average Order Value' = DIVIDE([Gross Revenue], [Total Orders], 0)
\t\tformatString: \\$#,0.00;(\\$#,0.00);\\$#,0.00
\t\tlineageTag: {uid()}

\tmeasure 'Cross-Sell Attach %' = DIVIDE(CALCULATE(COUNTROWS(order_items), order_items[is_primary_item] = 0), [Total Orders], 0)
\t\tformatString: 0.00%
\t\tlineageTag: {uid()}

\tmeasure 'Refund Rate %' = DIVIDE(COUNTROWS(order_item_refunds), COUNTROWS(order_items), 0)
\t\tformatString: 0.00%
\t\tlineageTag: {uid()}

\tmeasure 'Bounce Rate %' = DIVIDE(CALCULATE(COUNTROWS(website_sessions), website_sessions[Is Bounce] = 1), [Total Sessions], 0)
\t\tformatString: 0.00%
\t\tlineageTag: {uid()}

\tmeasure 'Repeat Sessions' = CALCULATE(COUNTROWS(website_sessions), website_sessions[is_repeat_session] = 1)
\t\tformatString: #,0
\t\tlineageTag: {uid()}

\tmeasure 'Repeat Session %' = DIVIDE([Repeat Sessions], [Total Sessions], 0)
\t\tformatString: 0.00%
\t\tlineageTag: {uid()}

\tmeasure 'Dynamic Selected Metric' = 
\t\tVAR SelectedMetricID = SELECTEDVALUE(_Param_Metric[MetricID], 1)
\t\tRETURN
\t\t\tSWITCH(
\t\t\t\tSelectedMetricID,
\t\t\t\t1, [Gross Revenue],
\t\t\t\t2, [Net Revenue],
\t\t\t\t3, [Gross Profit],
\t\t\t\t4, [Gross Margin %],
\t\t\t\t5, [Total Orders],
\t\t\t\t6, [Total Sessions],
\t\t\t\t7, [Conversion Rate %],
\t\t\t\t8, [Average Order Value],
\t\t\t\t9, [Cross-Sell Attach %],
\t\t\t\t10, [Refund Rate %],
\t\t\t\t[Gross Revenue]
\t\t\t)
\t\tlineageTag: {uid()}

\tmeasure 'Story Headline Text' = SELECTEDVALUE(_Param_Story[Headline], "Maven Fuzzy Factory: 3-Year Historical Growth Journey (2012-2015)")
\t\tlineageTag: {uid()}

\tmeasure 'Story Narrative Commentary' = SELECTEDVALUE(_Param_Story[Commentary], "Select a chapter from the storyline bar to explore how strategic marketing, UX testing, and product expansion transformed Maven Fuzzy Factory into a multimillion-dollar eCommerce brand.")
\t\tlineageTag: {uid()}
"""
dummy_col = col("Dummy", "int64", is_inferred=True, source_col="Value", format_str="0")
meas_part = f"""\tpartition _Measures = calculated
\t\tmode: import
\t\tsource = ROW("Dummy", 1)

\tannotation PBI_Id = {uid()}
"""
measures_tmdl = f"table _Measures\n\tlineageTag: {uid()}\n\n" + measures_body + "\n" + dummy_col + "\n" + meas_part

tables_dict = {
    "products": products_tmdl,
    "orders": orders_tmdl,
    "order_items": order_items_tmdl,
    "order_item_refunds": order_item_refunds_tmdl,
    "website_sessions": website_sessions_tmdl,
    "website_pageviews": website_pageviews_tmdl,
    "Dim_Date": dim_date_tmdl,
    "Dim_Channel": dim_channel_tmdl,
    "Dim_Lander": dim_lander_tmdl,
    "Dim_Customer": dim_customer_tmdl,
    "Basket_Pairs": basket_pairs_tmdl,
    "_Param_Metric": param_metric_tmdl,
    "_Param_Time": param_time_tmdl,
    "_Param_Dim": param_dim_tmdl,
    "_Param_Story": param_story_tmdl,
    "_Param_CVR_Lift": param_cvr_lift_tmdl,
    "_Param_Refund_Cut": param_refund_cut_tmdl,
    "_Param_Attach": param_attach_tmdl,
    "_Param_Target": param_target_tmdl,
    "_Param_LanderA": param_lander_a_tmdl,
    "_Param_LanderB": param_lander_b_tmdl,
    "_Param_CohortAge": param_cohort_age_tmdl,
    "_Dim_FunnelStep": dim_funnel_step_tmdl,
    "_Measures": measures_tmdl
}

for tbl_name, content in tables_dict.items():
    file_path = os.path.join(tables_dir, f"{tbl_name}.tmdl")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written: {tbl_name}.tmdl")

# Update model.tmdl
existing_refs = []
model_tmdl_path = os.path.join(base_dir, "model.tmdl")
if os.path.exists(model_tmdl_path):
    with open(model_tmdl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("ref table DateTableTemplate_") or line.startswith("ref table LocalDateTable_"):
                existing_refs.append(line.replace("ref table ", ""))

all_tables = list(tables_dict.keys()) + existing_refs
query_order = ["products", "orders", "order_items", "order_item_refunds", "website_sessions", "website_pageviews"]

model_content = f"""model Model
\tculture: en-US
\tdefaultPowerBIDataSourceVersion: powerBI_V3
\tsourceQueryCulture: en-US
\tvalueFilterBehavior: independent
\tdataAccessOptions
\t\tlegacyRedirects
\t\treturnErrorValuesAsNull

annotation __PBI_TimeIntelligenceEnabled = 1

annotation PBI_QueryOrder = {str(query_order).replace("'", '"')}

annotation PBI_ProTooling = ["DevMode"]

"""

for tbl in all_tables:
    model_content += f"ref table {tbl}\n"

model_content += "\nref cultureInfo en-US\n\n"

with open(model_tmdl_path, "w", encoding="utf-8") as f:
    f.write(model_content)
print("Updated: model.tmdl")

# Update relationships.tmdl
rel_list = [
    ("orders.'Order Date'", "Dim_Date.Date", True),
    ("order_items.'Order Date'", "Dim_Date.Date", False),
    ("website_sessions.'Session Date'", "Dim_Date.Date", True),
    ("order_item_refunds.'Refund Date'", "Dim_Date.Date", True),
    ("order_item_refunds.'Order Date'", "Dim_Date.Date", False),
    ("order_items.product_id", "products.product_id", True),
    ("orders.primary_product_id", "products.product_id", False),
    ("order_items.order_id", "orders.order_id", True),
    ("order_item_refunds.order_item_id", "order_items.order_item_id", False),
    ("orders.website_session_id", "website_sessions.website_session_id", False),
    ("website_pageviews.website_session_id", "website_sessions.website_session_id", True),
    # NOTE: no relationship to Dim_Customer - it is a calculated table derived from
    # website_sessions; relating them causes PFE_TM_RELATIONSHIP_END_COLUMN_INVALID.
]

existing_rel_str = """relationship 780db2d4-117d-491d-a3de-5f36d98d6a5d
	joinOnDateBehavior: datePartOnly
	fromColumn: order_item_refunds.created_at
	toColumn: LocalDateTable_1580720a-eb97-4948-bb47-5b731dcf40a7.Date

"""
rel_path = os.path.join(base_dir, "relationships.tmdl")
new_rel_str = existing_rel_str
for from_c, to_c, is_act in rel_list:
    r_id = uid()
    new_rel_str += f"relationship {r_id}\n"
    if not is_act:
        new_rel_str += f"\tisActive: false\n"
    new_rel_str += f"\tfromColumn: {from_c}\n"
    new_rel_str += f"\ttoColumn: {to_c}\n\n"

with open(rel_path, "w", encoding="utf-8") as f:
    f.write(new_rel_str)
print("Updated: relationships.tmdl")
print("ALL DONE SUCCESSFULLY!")
