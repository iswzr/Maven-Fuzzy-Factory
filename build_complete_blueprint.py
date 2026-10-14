import os
import uuid
import glob

def uid():
    return str(uuid.uuid4())

base_dir = r"f:\MAVEN DATA\Maven+Fuzzy+Factory\Maven Fuzzy Factory.SemanticModel\definition"
tables_dir = os.path.join(base_dir, "tables")

# ==============================================================================
# STEP 1: Delete redundant auto-date tables
# ==============================================================================
for f in glob.glob(os.path.join(tables_dir, "DateTableTemplate_*.tmdl")):
    os.remove(f)
    print("Deleted:", f)

for f in glob.glob(os.path.join(tables_dir, "LocalDateTable_*.tmdl")):
    os.remove(f)
    print("Deleted:", f)

# Helper for TMDL column definition
def col(name, data_type, is_source=True, source_col=None, is_inferred=False, 
        format_str=None, dax_calc=None, is_hidden=False, is_key=False, 
        sort_by=None, data_category=None):
    quoted_name = f"'{name}'" if any(c in name for c in " %$-#/") else name
    lines = []
    if dax_calc:
        lines.append(f"\tcolumn {quoted_name} = {dax_calc}")
    else:
        lines.append(f"\tcolumn {quoted_name}")
    lines.append(f"\t\tdataType: {data_type}")
    if is_hidden:
        lines.append(f"\t\tisHidden")
    if is_key:
        lines.append(f"\t\tisKey")
    if format_str:
        lines.append(f"\t\tformatString: {format_str}")
    if data_category:
        lines.append(f"\t\tdataCategory: {data_category}")
    if sort_by:
        q_sort = f"'{sort_by}'" if any(c in sort_by for c in " %$-#/") else sort_by
        lines.append(f"\t\tsortByColumn: {q_sort}")
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


# ==============================================================================
# 1. website_pageviews (Fact_Pageviews)
# ==============================================================================
pv_cols = [
    col("website_pageview_id", "int64", is_source=True, is_hidden=True, format_str="0"),
    col("created_at", "dateTime", is_source=True, is_hidden=True, format_str="General Date"),
    col("website_session_id", "int64", is_source=True, is_hidden=True, format_str="0"),
    col("pageview_url", "string", is_source=True),
    col("Pageview Date", "dateTime", is_source=True, source_col="Pageview Date", format_str="yyyy-MM-dd"),
    col("Funnel Step", "int64", is_source=True, source_col="Funnel Step", format_str="0"),
    col("Page Category", "string", is_source=True, source_col="Page Category")
]

pv_m = '''\tpartition website_pageviews = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t  Source = Csv.Document(File.Contents("F:\\MAVEN DATA\\Maven+Fuzzy+Factory\\website_pageviews.csv"), [Delimiter = ",", Columns = 4, QuoteStyle = QuoteStyle.None]),
\t\t\t\t  #"Promoted headers" = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
\t\t\t\t  #"Changed column type" = Table.TransformColumnTypes(#"Promoted headers", {{"website_pageview_id", Int64.Type}, {"created_at", type datetime}, {"website_session_id", Int64.Type}, {"pageview_url", type text}}),
\t\t\t\t  #"Added Pageview Date" = Table.AddColumn(#"Changed column type", "Pageview Date", each DateTime.Date([created_at]), type date),
\t\t\t\t  #"Added Funnel Step" = Table.AddColumn(#"Added Pageview Date", "Funnel Step", each if [pageview_url] = "/home" or Text.StartsWith([pageview_url], "/lander") then 1 else if [pageview_url] = "/products" then 2 else if Text.StartsWith([pageview_url], "/the-") then 3 else if [pageview_url] = "/cart" then 4 else if [pageview_url] = "/shipping" then 5 else if Text.StartsWith([pageview_url], "/billing") then 6 else if [pageview_url] = "/thank-you-for-your-order" then 7 else null, Int64.Type),
\t\t\t\t  #"Added Page Category" = Table.AddColumn(#"Added Funnel Step", "Page Category", each if List.Contains({"/home", "/lander-1", "/lander-2", "/lander-3", "/lander-4", "/lander-5"}, [pageview_url]) then "Landing Page" else if [pageview_url] = "/products" then "Catalog" else if List.Contains({"/the-original-mr-fuzzy", "/the-forever-love-bear", "/the-birthday-sugar-panda", "/the-hudson-river-mini-bear"}, [pageview_url]) then "Product Detail" else if List.Contains({"/cart", "/shipping", "/billing", "/billing-2"}, [pageview_url]) then "Checkout Funnel" else if [pageview_url] = "/thank-you-for-your-order" then "Conversion" else "Other", type text)
\t\t\t\tin
\t\t\t\t  #"Added Page Category"

\tannotation PBI_ResultType = Table
'''
website_pageviews_tmdl = f"table website_pageviews\n\tlineageTag: {uid()}\n\n" + "\n".join(pv_cols) + "\n" + pv_m


# ==============================================================================
# 2. website_sessions (Fact_Sessions)
# ==============================================================================
sessions_cols = [
    col("website_session_id", "int64", is_source=True, is_hidden=True, format_str="0"),
    col("created_at", "dateTime", is_source=True, is_hidden=True, format_str="General Date"),
    col("user_id", "int64", is_source=True, is_hidden=True, format_str="0"),
    col("is_repeat_session", "int64", is_source=True, is_hidden=True, format_str="0"),
    col("utm_source", "string", is_source=True),
    col("utm_campaign", "string", is_source=True),
    col("utm_content", "string", is_source=True),
    col("device_type", "string", is_source=True),
    col("http_referer", "string", is_source=True),
    col("Session Date", "dateTime", is_source=True, source_col="Session Date", format_str="yyyy-MM-dd"),
    col("Visit Type", "string", is_source=True, source_col="Visit Type"),
    col("Channel Grouping", "string", is_source=True, source_col="Channel Grouping"),
    col("Traffic Type", "string", is_source=True, source_col="Traffic Type"),
    col("Chapter ID", "int64", is_source=True, source_col="Chapter ID", format_str="0"),
    col("Landing Page", "string", dax_calc="CALCULATE(SELECTEDVALUE(website_pageviews[pageview_url]), TOPN(1, RELATEDTABLE(website_pageviews), website_pageviews[website_pageview_id], ASC))"),
    col("Pageviews", "int64", dax_calc="COUNTROWS(RELATEDTABLE(website_pageviews))", format_str="0"),
    col("Is Bounce", "int64", dax_calc="IF([Pageviews] = 1, 1, 0)", format_str="0"),
    col("Funnel Depth", "int64", dax_calc="CALCULATE(MAX(website_pageviews[Funnel Step]), RELATEDTABLE(website_pageviews))", format_str="0"),
    col("Billing Variant", "string", dax_calc='IF(CALCULATE(COUNTROWS(website_pageviews), website_pageviews[pageview_url] = "/billing-2", RELATEDTABLE(website_pageviews)) > 0, "billing-2", IF(CALCULATE(COUNTROWS(website_pageviews), website_pageviews[pageview_url] = "/billing", RELATEDTABLE(website_pageviews)) > 0, "billing", BLANK()))'),
    col("Days Since First Session", "int64", dax_calc="VAR first = CALCULATE(MIN(website_sessions[Session Date]), ALLEXCEPT(website_sessions, website_sessions[user_id])) RETURN DATEDIFF(first, website_sessions[Session Date], DAY)", format_str="0")
]

sessions_m = '''\tpartition website_sessions = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t  Source = Csv.Document(File.Contents("F:\\MAVEN DATA\\Maven+Fuzzy+Factory\\website_sessions.csv"), [Delimiter = ",", Columns = 9, QuoteStyle = QuoteStyle.None]),
\t\t\t\t  #"Promoted headers" = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
\t\t\t\t  #"Changed column type" = Table.TransformColumnTypes(#"Promoted headers", {{"website_session_id", Int64.Type}, {"created_at", type datetime}, {"user_id", Int64.Type}, {"is_repeat_session", Int64.Type}, {"utm_source", type text}, {"utm_campaign", type text}, {"utm_content", type text}, {"device_type", type text}, {"http_referer", type text}}),
\t\t\t\t  #"Replaced NULLs" = Table.ReplaceValue(#"Changed column type", "NULL", null, Replacer.ReplaceValue, {"utm_source", "utm_campaign", "utm_content", "http_referer"}),
\t\t\t\t  #"Added Session Date" = Table.AddColumn(#"Replaced NULLs", "Session Date", each DateTime.Date([created_at]), type date),
\t\t\t\t  #"Added Visit Type" = Table.AddColumn(#"Added Session Date", "Visit Type", each if [is_repeat_session] = 1 then "Repeat" else "New", type text),
\t\t\t\t  #"Added Channel Grouping" = Table.AddColumn(#"Added Visit Type", "Channel Grouping", each if [utm_source] = null and [http_referer] = null then "Direct" else if [utm_source] = null then "Organic Search" else if [utm_source] = "gsearch" and [utm_campaign] = "brand" then "Google Brand" else if [utm_source] = "gsearch" and [utm_campaign] = "nonbrand" then "Google Nonbrand" else if [utm_source] = "bsearch" and [utm_campaign] = "brand" then "Bing Brand" else if [utm_source] = "bsearch" and [utm_campaign] = "nonbrand" then "Bing Nonbrand" else if [utm_source] = "socialbook" then "Paid Social" else "Other", type text),
\t\t\t\t  #"Added Traffic Type" = Table.AddColumn(#"Added Channel Grouping", "Traffic Type", each if [Channel Grouping] = "Direct" then "Direct" else if [Channel Grouping] = "Organic Search" then "Organic" else "Paid", type text),
\t\t\t\t  #"Added Chapter ID" = Table.AddColumn(#"Added Traffic Type", "Chapter ID", each if [created_at] >= #datetime(2015, 1, 1, 0, 0, 0) then 5 else if [created_at] >= #datetime(2014, 2, 1, 0, 0, 0) then 4 else if [created_at] >= #datetime(2013, 1, 1, 0, 0, 0) then 3 else if [created_at] >= #datetime(2012, 9, 1, 0, 0, 0) then 2 else 1, Int64.Type)
\t\t\t\tin
\t\t\t\t  #"Added Chapter ID"

\tannotation PBI_ResultType = Table
'''
website_sessions_tmdl = f"table website_sessions\n\tlineageTag: {uid()}\n\n" + "\n".join(sessions_cols) + "\n" + sessions_m


# ==============================================================================
# 3. orders (Fact_Orders)
# ==============================================================================
orders_cols = [
    col("order_id", "int64", is_source=True, is_hidden=True, format_str="0"),
    col("created_at", "dateTime", is_source=True, is_hidden=True, format_str="General Date"),
    col("website_session_id", "int64", is_source=True, is_hidden=True, format_str="0"),
    col("user_id", "int64", is_source=True, is_hidden=True, format_str="0"),
    col("primary_product_id", "int64", is_source=True, is_hidden=True, format_str="0"),
    col("items_purchased", "int64", is_source=True, format_str="0"),
    col("price_usd", "double", is_source=True, format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("cogs_usd", "double", is_source=True, format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("Order Date", "dateTime", is_source=True, source_col="Order Date", format_str="yyyy-MM-dd"),
    col("Order Seq", "int64", dax_calc="VAR o = orders[order_id] RETURN CALCULATE(COUNTROWS(orders), ALLEXCEPT(orders, orders[user_id]), orders[order_id] <= o)", format_str="0"),
    col("Is Repeat Order", "int64", dax_calc="IF(orders[Order Seq] > 1, 1, 0)", format_str="0"),
    col("First Order Date", "dateTime", dax_calc="CALCULATE(MIN(orders[Order Date]), ALLEXCEPT(orders, orders[user_id]))", format_str="yyyy-MM-dd"),
    col("Cohort Month", "dateTime", dax_calc="DATE(YEAR(orders[First Order Date]), MONTH(orders[First Order Date]), 1)", format_str="yyyy-MM"),
    col("Months Since First", "int64", dax_calc="DATEDIFF(orders[Cohort Month], DATE(YEAR(orders[Order Date]), MONTH(orders[Order Date]), 1), MONTH)", format_str="0"),
    col("Basket Type", "string", is_source=True, source_col="Basket Type"),
    col("Margin $", "double", is_source=True, source_col="Margin $", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("Margin %", "double", is_source=True, source_col="Margin %", format_str="0.00%")
]

orders_m = '''\tpartition orders = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t  Source = Csv.Document(File.Contents("F:\\MAVEN DATA\\Maven+Fuzzy+Factory\\orders.csv"), [Delimiter = ",", Columns = 8, QuoteStyle = QuoteStyle.None]),
\t\t\t\t  #"Promoted headers" = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
\t\t\t\t  #"Changed column type" = Table.TransformColumnTypes(#"Promoted headers", {{"order_id", Int64.Type}, {"created_at", type datetime}, {"website_session_id", Int64.Type}, {"user_id", Int64.Type}, {"primary_product_id", Int64.Type}, {"items_purchased", Int64.Type}, {"price_usd", type number}, {"cogs_usd", type number}}),
\t\t\t\t  #"Added Order Date" = Table.AddColumn(#"Changed column type", "Order Date", each DateTime.Date([created_at]), type date),
\t\t\t\t  #"Added Basket Type" = Table.AddColumn(#"Added Order Date", "Basket Type", each if [items_purchased] = 1 then "1 item" else "2 items", type text),
\t\t\t\t  #"Added Margin $" = Table.AddColumn(#"Added Basket Type", "Margin $", each [price_usd] - [cogs_usd], type number),
\t\t\t\t  #"Added Margin %" = Table.AddColumn(#"Added Margin $", "Margin %", each if [price_usd] = 0 or [price_usd] = null then 0 else ([price_usd] - [cogs_usd]) / [price_usd], type number)
\t\t\t\tin
\t\t\t\t  #"Added Margin %"

\tannotation PBI_ResultType = Table
'''
orders_tmdl = f"table orders\n\tlineageTag: {uid()}\n\n" + "\n".join(orders_cols) + "\n" + orders_m


# ==============================================================================
# 4. order_items (Fact_OrderItems)
# ==============================================================================
order_items_cols = [
    col("order_item_id", "int64", is_source=True, is_hidden=True, format_str="0"),
    col("created_at", "dateTime", is_source=True, is_hidden=True, format_str="General Date"),
    col("order_id", "int64", is_source=True, is_hidden=True, format_str="0"),
    col("product_id", "int64", is_source=True, is_hidden=True, format_str="0"),
    col("is_primary_item", "int64", is_source=True, format_str="0"),
    col("price_usd", "double", is_source=True, format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("cogs_usd", "double", is_source=True, format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("Order Date", "dateTime", is_source=True, source_col="Order Date", format_str="yyyy-MM-dd"),
    col("Item Role", "string", is_source=True, source_col="Item Role"),
    col("Primary Product ID", "int64", dax_calc="RELATED(orders[primary_product_id])", is_hidden=True, format_str="0"),
    col("Pair Label", "string", dax_calc='IF(order_items[is_primary_item] = 0, LOOKUPVALUE(products[product_name], products[product_id], order_items[Primary Product ID]) & " → " & RELATED(products[product_name]))'),
    col("Margin $", "double", is_source=True, source_col="Margin $", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("Margin %", "double", is_source=True, source_col="Margin %", format_str="0.00%")
]

order_items_m = '''\tpartition order_items = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t  Source = Csv.Document(File.Contents("F:\\MAVEN DATA\\Maven+Fuzzy+Factory\\order_items.csv"), [Delimiter = ",", Columns = 7, QuoteStyle = QuoteStyle.None]),
\t\t\t\t  #"Promoted headers" = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
\t\t\t\t  #"Changed column type" = Table.TransformColumnTypes(#"Promoted headers", {{"order_item_id", Int64.Type}, {"created_at", type datetime}, {"order_id", Int64.Type}, {"product_id", Int64.Type}, {"is_primary_item", Int64.Type}, {"price_usd", type number}, {"cogs_usd", type number}}),
\t\t\t\t  #"Added Order Date" = Table.AddColumn(#"Changed column type", "Order Date", each DateTime.Date([created_at]), type date),
\t\t\t\t  #"Added Item Role" = Table.AddColumn(#"Added Order Date", "Item Role", each if [is_primary_item] = 1 then "Primary" else "Cross-sell", type text),
\t\t\t\t  #"Added Margin $" = Table.AddColumn(#"Added Item Role", "Margin $", each [price_usd] - [cogs_usd], type number),
\t\t\t\t  #"Added Margin %" = Table.AddColumn(#"Added Margin $", "Margin %", each if [price_usd] = 0 or [price_usd] = null then 0 else ([price_usd] - [cogs_usd]) / [price_usd], type number)
\t\t\t\tin
\t\t\t\t  #"Added Margin %"

\tannotation PBI_ResultType = Table
'''
order_items_tmdl = f"table order_items\n\tlineageTag: {uid()}\n\n" + "\n".join(order_items_cols) + "\n" + order_items_m


# ==============================================================================
# 5. order_item_refunds (Fact_Refunds) - Cleaned of LocalDateTable variation
# ==============================================================================
refunds_cols = [
    col("order_item_refund_id", "int64", is_source=True, is_hidden=True, format_str="0"),
    col("created_at", "dateTime", is_source=True, is_hidden=True, format_str="General Date"),
    col("order_item_id", "int64", is_source=True, is_hidden=True, format_str="0"),
    col("order_id", "int64", is_source=True, is_hidden=True, format_str="0"),
    col("refund_amount_usd", "double", is_source=True, format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("Refund Date", "dateTime", is_source=True, source_col="Refund Date", format_str="yyyy-MM-dd"),
    col("Order Date", "dateTime", dax_calc="RELATED(order_items[Order Date])", format_str="yyyy-MM-dd"),
    col("Refund Lag Days", "int64", dax_calc="DATEDIFF(order_item_refunds[Order Date], order_item_refunds[Refund Date], DAY)", format_str="0"),
    col("Lag Bucket", "string", dax_calc='SWITCH(TRUE(), order_item_refunds[Refund Lag Days] <= 5, "2–5 d", order_item_refunds[Refund Lag Days] <= 10, "6–10 d", "11–16 d")')
]

refunds_m = '''\tpartition order_item_refunds = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t  Source = Csv.Document(File.Contents("F:\\MAVEN DATA\\Maven+Fuzzy+Factory\\order_item_refunds.csv"), [Delimiter = ",", Columns = 5, QuoteStyle = QuoteStyle.None]),
\t\t\t\t  #"Promoted headers" = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
\t\t\t\t  #"Changed column type" = Table.TransformColumnTypes(#"Promoted headers", {{"order_item_refund_id", Int64.Type}, {"created_at", type datetime}, {"order_item_id", Int64.Type}, {"order_id", Int64.Type}, {"refund_amount_usd", type number}}),
\t\t\t\t  #"Added Refund Date" = Table.AddColumn(#"Changed column type", "Refund Date", each DateTime.Date([created_at]), type date)
\t\t\t\tin
\t\t\t\t  #"Added Refund Date"

\tannotation PBI_ResultType = Table
'''
order_item_refunds_tmdl = f"table order_item_refunds\n\tlineageTag: {uid()}\n\n" + "\n".join(refunds_cols) + "\n" + refunds_m


# ==============================================================================
# 6. products (Dim_Product)
# ==============================================================================
products_cols = [
    col("product_id", "int64", is_source=True, is_key=True, is_hidden=True, format_str="0"),
    col("created_at", "dateTime", is_source=True, is_hidden=True, format_str="General Date"),
    col("product_name", "string", is_source=True),
    col("Unit Price", "double", is_source=True, source_col="Unit Price", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("Unit COGS", "double", is_source=True, source_col="Unit COGS", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("Unit Margin %", "double", is_source=True, source_col="Unit Margin %", format_str="0.00%"),
    col("Color", "string", is_source=True, source_col="Color")
]

products_m = '''\tpartition products = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t  Source = Csv.Document(File.Contents("F:\\MAVEN DATA\\Maven+Fuzzy+Factory\\products.csv"), [Delimiter = ",", Columns = 3, QuoteStyle = QuoteStyle.None]),
\t\t\t\t  #"Promoted headers" = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
\t\t\t\t  #"Changed column type" = Table.TransformColumnTypes(#"Promoted headers", {{"product_id", Int64.Type}, {"created_at", type datetime}, {"product_name", type text}}),
\t\t\t\t  #"Added Unit Price" = Table.AddColumn(#"Changed column type", "Unit Price", each if [product_id] = 1 then 49.99 else if [product_id] = 2 then 59.99 else if [product_id] = 3 then 45.99 else 29.99, type number),
\t\t\t\t  #"Added Unit COGS" = Table.AddColumn(#"Added Unit Price", "Unit COGS", each if [product_id] = 1 then 19.49 else if [product_id] = 2 then 22.49 else if [product_id] = 3 then 14.49 else 9.49, type number),
\t\t\t\t  #"Added Unit Margin %" = Table.AddColumn(#"Added Unit COGS", "Unit Margin %", each ([#"Unit Price"] - [#"Unit COGS"]) / [#"Unit Price"], type number),
\t\t\t\t  #"Added Color" = Table.AddColumn(#"Added Unit Margin %", "Color", each if [product_id] = 1 then "#60A5FA" else if [product_id] = 2 then "#FB7185" else if [product_id] = 3 then "#FBBF24" else "#2DD4BF", type text)
\t\t\t\tin
\t\t\t\t  #"Added Color"

\tannotation PBI_ResultType = Table
'''
products_tmdl = f"table products\n\tlineageTag: {uid()}\n\n" + "\n".join(products_cols) + "\n" + products_m


# ==============================================================================
# 7. Dim_PrimaryProduct (New role-playing dimension)
# ==============================================================================
primary_prod_cols = [
    col("Primary product_id", "int64", is_source=True, is_key=True, is_hidden=True, format_str="0"),
    col("Primary created_at", "dateTime", is_source=True, is_hidden=True, format_str="General Date"),
    col("Primary product_name", "string", is_source=True),
    col("Primary Unit Price", "double", is_source=True, source_col="Primary Unit Price", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("Primary Unit COGS", "double", is_source=True, source_col="Primary Unit COGS", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("Primary Unit Margin %", "double", is_source=True, source_col="Primary Unit Margin %", format_str="0.00%"),
    col("Primary Color", "string", is_source=True, source_col="Primary Color")
]

primary_prod_m = '''\tpartition Dim_PrimaryProduct = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t  Source = Csv.Document(File.Contents("F:\\MAVEN DATA\\Maven+Fuzzy+Factory\\products.csv"), [Delimiter = ",", Columns = 3, QuoteStyle = QuoteStyle.None]),
\t\t\t\t  #"Promoted headers" = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
\t\t\t\t  #"Changed column type" = Table.TransformColumnTypes(#"Promoted headers", {{"product_id", Int64.Type}, {"created_at", type datetime}, {"product_name", type text}}),
\t\t\t\t  #"Renamed Columns" = Table.RenameColumns(#"Changed column type", {{"product_id", "Primary product_id"}, {"created_at", "Primary created_at"}, {"product_name", "Primary product_name"}}),
\t\t\t\t  #"Added Unit Price" = Table.AddColumn(#"Renamed Columns", "Primary Unit Price", each if [#"Primary product_id"] = 1 then 49.99 else if [#"Primary product_id"] = 2 then 59.99 else if [#"Primary product_id"] = 3 then 45.99 else 29.99, type number),
\t\t\t\t  #"Added Unit COGS" = Table.AddColumn(#"Added Unit Price", "Primary Unit COGS", each if [#"Primary product_id"] = 1 then 19.49 else if [#"Primary product_id"] = 2 then 22.49 else if [#"Primary product_id"] = 3 then 14.49 else 9.49, type number),
\t\t\t\t  #"Added Unit Margin %" = Table.AddColumn(#"Added Unit COGS", "Primary Unit Margin %", each ([#"Primary Unit Price"] - [#"Primary Unit COGS"]) / [#"Primary Unit Price"], type number),
\t\t\t\t  #"Added Color" = Table.AddColumn(#"Added Unit Margin %", "Primary Color", each if [#"Primary product_id"] = 1 then "#60A5FA" else if [#"Primary product_id"] = 2 then "#FB7185" else if [#"Primary product_id"] = 3 then "#FBBF24" else "#2DD4BF", type text)
\t\t\t\tin
\t\t\t\t  #"Added Color"

\tannotation PBI_ResultType = Table
'''
dim_primary_product_tmdl = f"table Dim_PrimaryProduct\n\tlineageTag: {uid()}\n\n" + "\n".join(primary_prod_cols) + "\n" + primary_prod_m


# ==============================================================================
# 8. Dim_Date (Official Date Table)
# ==============================================================================
dim_date_cols = [
    col("Date", "dateTime", is_inferred=True, is_key=True, format_str="yyyy-MM-dd"),
    col("Year", "int64", is_inferred=True, format_str="0"),
    col("Quarter", "string", is_inferred=True),
    col("Month #", "int64", is_inferred=True, format_str="0"),
    col("Month", "string", is_inferred=True, sort_by="Month #"),
    col("Month Start", "dateTime", is_inferred=True, format_str="yyyy-MM-dd"),
    col("Is Weekend", "boolean", is_inferred=True),
    col("Is Partial Month", "boolean", is_inferred=True),
    col("Chapter ID", "int64", is_inferred=True, format_str="0")
]

dim_date_part = '''\tpartition Dim_Date = calculated
\t\tmode: import
\t\tsource =
\t\t\tADDCOLUMNS(
\t\t\t    CALENDAR(DATE(2012,3,1), DATE(2015,3,31)),
\t\t\t    "Year", YEAR([Date]),
\t\t\t    "Quarter", "Q" & QUARTER([Date]),
\t\t\t    "Month #", MONTH([Date]),
\t\t\t    "Month", FORMAT([Date], "MMM"),
\t\t\t    "Month Start", DATE(YEAR([Date]), MONTH([Date]), 1),
\t\t\t    "Is Weekend", WEEKDAY([Date], 2) > 5,
\t\t\t    "Is Partial Month", [Date] >= DATE(2015, 3, 1),
\t\t\t    "Chapter ID", SWITCH(TRUE(),
\t\t\t        [Date] <= DATE(2012,8,31), 1,
\t\t\t        [Date] <= DATE(2012,12,31), 2,
\t\t\t        [Date] <= DATE(2014,1,31), 3,
\t\t\t        [Date] <= DATE(2014,12,31), 4,
\t\t\t        5
\t\t\t    )
\t\t\t)

\tannotation PBI_Id = 7a83d47a-24c1-4ca3-bc8e-152e043a6d20
'''
dim_date_tmdl = f"table Dim_Date\n\tlineageTag: {uid()}\n\tdataCategory: Time\n\n" + "\n".join(dim_date_cols) + "\n" + dim_date_part


# ==============================================================================
# 9. Dim_Channel
# ==============================================================================
dim_channel_cols = [
    col("Channel Grouping", "string", is_inferred=True, is_key=True),
    col("Traffic Type", "string", is_inferred=True),
    col("Campaign Type", "string", is_inferred=True),
    col("Color", "string", is_inferred=True)
]

dim_channel_part = '''\tpartition Dim_Channel = calculated
\t\tmode: import
\t\tsource =
\t\t\tDATATABLE(
\t\t\t    "Channel Grouping", STRING, "Traffic Type", STRING, "Campaign Type", STRING, "Color", STRING,
\t\t\t    {
\t\t\t        {"Google Nonbrand", "Paid", "Nonbrand", "#60A5FA"},
\t\t\t        {"Bing Nonbrand", "Paid", "Nonbrand", "#22D3EE"},
\t\t\t        {"Google Brand", "Paid", "Brand", "#A78BFA"},
\t\t\t        {"Bing Brand", "Paid", "Brand", "#C4B5FD"},
\t\t\t        {"Paid Social", "Paid", "Social", "#FB7185"},
\t\t\t        {"Organic Search", "Organic", "Organic", "#34D399"},
\t\t\t        {"Direct", "Direct", "Direct", "#FBBF24"}
\t\t\t    }
\t\t\t)

\tannotation PBI_Id = 0db3b345-8cb5-41ca-84a5-bfc7aaa60573
'''
dim_channel_tmdl = f"table Dim_Channel\n\tlineageTag: {uid()}\n\n" + "\n".join(dim_channel_cols) + "\n" + dim_channel_part


# ==============================================================================
# 10. Dim_Lander
# ==============================================================================
dim_lander_cols = [
    col("Landing Page", "string", is_inferred=True, is_key=True),
    col("Test Role", "string", is_inferred=True)
]

dim_lander_part = '''\tpartition Dim_Lander = calculated
\t\tmode: import
\t\tsource =
\t\t\tDATATABLE(
\t\t\t    "Landing Page", STRING, "Test Role", STRING,
\t\t\t    {
\t\t\t        {"/home", "Baseline"},
\t\t\t        {"/lander-1", "Challenger"},
\t\t\t        {"/lander-2", "Challenger"},
\t\t\t        {"/lander-3", "Challenger"},
\t\t\t        {"/lander-4", "Challenger"},
\t\t\t        {"/lander-5", "Challenger"}
\t\t\t    }
\t\t\t)

\tannotation PBI_Id = e9b6e8f2-e3b5-4fab-8162-fc15b943a3e8
'''
dim_lander_tmdl = f"table Dim_Lander\n\tlineageTag: {uid()}\n\n" + "\n".join(dim_lander_cols) + "\n" + dim_lander_part


# ==============================================================================
# 11. Dim_Customer (Native M table for 394K distinct users)
# ==============================================================================
dim_cust_cols = [
    col("user_id", "int64", is_source=True, is_key=True, is_hidden=True, format_str="0"),
    col("First Session", "dateTime", dax_calc="CALCULATE(MIN(website_sessions[Session Date]))", format_str="yyyy-MM-dd"),
    col("Orders", "int64", dax_calc="CALCULATE(COUNTROWS(orders))", format_str="0"),
    col("User Segment", "string", dax_calc='SWITCH(TRUE(), [Orders] = 0, "Browser", [Orders] = 1, "One-time buyer", "Repeat buyer")')
]

dim_cust_m = '''\tpartition Dim_Customer = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t  Source = Csv.Document(File.Contents("F:\\MAVEN DATA\\Maven+Fuzzy+Factory\\website_sessions.csv"), [Delimiter = ",", Columns = 9, QuoteStyle = QuoteStyle.None]),
\t\t\t\t  #"Promoted headers" = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
\t\t\t\t  #"Kept User" = Table.SelectColumns(#"Promoted headers", {"user_id"}),
\t\t\t\t  #"Distinct User" = Table.Distinct(#"Kept User"),
\t\t\t\t  #"Changed Type" = Table.TransformColumnTypes(#"Distinct User", {{"user_id", Int64.Type}})
\t\t\t\tin
\t\t\t\t  #"Changed Type"

\tannotation PBI_ResultType = Table
'''
dim_customer_tmdl = f"table Dim_Customer\n\tlineageTag: {uid()}\n\n" + "\n".join(dim_cust_cols) + "\n" + dim_cust_m


# ==============================================================================
# 12. Sens_Grid (New table for P7 heatmap)
# ==============================================================================
sens_grid_cols = [
    col("CVR Step", "double", is_inferred=True, format_str="0.0%"),
    col("XSell Step", "double", is_inferred=True, format_str="0.0%")
]

sens_grid_part = '''\tpartition Sens_Grid = calculated
\t\tmode: import
\t\tsource =
\t\t\tGENERATECROSSJOIN(
\t\t\t    SELECTCOLUMNS(GENERATESERIES(0, 0.4, 0.1),  "CVR Step",   [Value]),
\t\t\t    SELECTCOLUMNS(GENERATESERIES(0, 0.2, 0.05), "XSell Step", [Value])
\t\t\t)

\tannotation PBI_Id = 4f981dc8-3482-411a-8bc2-7d23d8c919a0
'''
sens_grid_tmdl = f"table Sens_Grid\n\tlineageTag: {uid()}\n\n" + "\n".join(sens_grid_cols) + "\n" + sens_grid_part


# ==============================================================================
# 13. _Dim_FunnelStep
# ==============================================================================
funnel_step_cols = [
    col("StepID", "int64", is_inferred=True, format_str="0"),
    col("Step", "string", is_inferred=True, sort_by="StepID"),
    col("StepNumber", "int64", is_inferred=True, format_str="0"),
    col("StepName", "string", is_inferred=True, sort_by="StepNumber")
]

funnel_step_part = '''\tpartition _Dim_FunnelStep = calculated
\t\tmode: import
\t\tsource =
\t\t\tDATATABLE(
\t\t\t    "StepID", INTEGER, "Step", STRING, "StepNumber", INTEGER, "StepName", STRING,
\t\t\t    {
\t\t\t        {1, "Landing", 1, "1. Landing"},
\t\t\t        {2, "Products", 2, "2. Products"},
\t\t\t        {3, "Product page", 3, "3. Product page"},
\t\t\t        {4, "Cart", 4, "4. Cart"},
\t\t\t        {5, "Shipping", 5, "5. Shipping"},
\t\t\t        {6, "Billing", 6, "6. Billing"},
\t\t\t        {7, "Order placed", 7, "7. Order placed"}
\t\t\t    }
\t\t\t)

\tannotation PBI_Id = d1481fec-e71a-4281-b5cb-19f8ca730a81
'''
dim_funnel_step_tmdl = f"table _Dim_FunnelStep\n\tlineageTag: {uid()}\n\n" + "\n".join(funnel_step_cols) + "\n" + funnel_step_part


# ==============================================================================
# 14. _Param_Metric
# ==============================================================================
param_metric_cols = [
    col("MetricID", "int64", is_inferred=True, format_str="0"),
    col("MetricName", "string", is_inferred=True),
    col("Category", "string", is_inferred=True)
]

param_metric_part = '''\tpartition _Param_Metric = calculated
\t\tmode: import
\t\tsource =
\t\t\tDATATABLE("MetricID", INTEGER, "MetricName", STRING, "Category", STRING,
\t\t\t{
\t\t\t    {1, "Gross Revenue ($)", "Financial"},
\t\t\t    {2, "Net Revenue ($)", "Financial"},
\t\t\t    {3, "Gross Margin ($)", "Financial"},
\t\t\t    {4, "Gross Margin %", "Financial"},
\t\t\t    {5, "Total Orders", "Volume"},
\t\t\t    {6, "Total Sessions", "Traffic"},
\t\t\t    {7, "Conversion Rate %", "Efficiency"},
\t\t\t    {8, "Average Order Value ($)", "Basket"},
\t\t\t    {9, "Cross-Sell Attach %", "Basket"},
\t\t\t    {10, "Refund Rate %", "Quality"}
\t\t\t})

\tannotation PBI_Id = 7cb019ef-e812-42da-be12-92fc18df3948
'''
param_metric_tmdl = f"table _Param_Metric\n\tlineageTag: {uid()}\n\n" + "\n".join(param_metric_cols) + "\n" + param_metric_part


# ==============================================================================
# 15. _Param_Time
# ==============================================================================
param_time_cols = [
    col("TimeModeID", "int64", is_inferred=True, format_str="0"),
    col("TimeModeName", "string", is_inferred=True)
]

param_time_part = '''\tpartition _Param_Time = calculated
\t\tmode: import
\t\tsource =
\t\t\tDATATABLE("TimeModeID", INTEGER, "TimeModeName", STRING,
\t\t\t{
\t\t\t    {1, "Current Actuals"},
\t\t\t    {2, "Previous Period (PoP)"},
\t\t\t    {3, "Previous Year (YoY)"},
\t\t\t    {4, "YoY Variance (abs)"},
\t\t\t    {5, "YoY Variance %"},
\t\t\t    {6, "Rolling 30D (3M here)"}
\t\t\t})

\tannotation PBI_Id = 5ea933b8-62da-4fb1-b1e4-84c1f9f6e520
'''
param_time_tmdl = f"table _Param_Time\n\tlineageTag: {uid()}\n\n" + "\n".join(param_time_cols) + "\n" + param_time_part


# ==============================================================================
# 16. _Param_Dim (Axis Bridge Table)
# ==============================================================================
param_dim_cols = [
    col("DimID", "int64", is_inferred=True, format_str="0"),
    col("DimName", "string", is_inferred=True),
    col("Member", "string", is_inferred=True)
]

param_dim_part = '''\tpartition _Param_Dim = calculated
\t\tmode: import
\t\tsource =
\t\t\tUNION(
\t\t\t  SELECTCOLUMNS(Dim_Channel, "DimID", 1, "DimName", "Marketing Channel", "Member", Dim_Channel[Channel Grouping]),
\t\t\t  SELECTCOLUMNS(VALUES(website_sessions[device_type]), "DimID", 2, "DimName", "Device", "Member", website_sessions[device_type]),
\t\t\t  SELECTCOLUMNS(products, "DimID", 3, "DimName", "Product", "Member", products[product_name]),
\t\t\t  SELECTCOLUMNS(Dim_Lander, "DimID", 4, "DimName", "Landing Page", "Member", Dim_Lander[Landing Page]),
\t\t\t  SELECTCOLUMNS(DISTINCT(Dim_Channel[Campaign Type]), "DimID", 5, "DimName", "Campaign", "Member", Dim_Channel[Campaign Type])
\t\t\t)

\tannotation PBI_Id = 25da3c22-b9e7-492c-8064-f6b95c378910
'''
param_dim_tmdl = f"table _Param_Dim\n\tlineageTag: {uid()}\n\n" + "\n".join(param_dim_cols) + "\n" + param_dim_part


# ==============================================================================
# 17. _Param_Story
# ==============================================================================
param_story_cols = [
    col("ChapterID", "int64", is_inferred=True, format_str="0"),
    col("ChapterName", "string", is_inferred=True),
    col("Timeframe", "string", is_inferred=True),
    col("Headline", "string", is_inferred=True),
    col("Commentary", "string", is_inferred=True),
    col("StartDate", "dateTime", is_inferred=True, format_str="yyyy-MM-dd"),
    col("EndDate", "dateTime", is_inferred=True, format_str="yyyy-MM-dd")
]

param_story_part = '''\tpartition _Param_Story = calculated
\t\tmode: import
\t\tsource = DATATABLE("ChapterID", INTEGER, "ChapterName", STRING, "Timeframe", STRING, "Headline", STRING, "Commentary", STRING, "StartDate", DATETIME, "EndDate", DATETIME, {{0, "All 3 Years", "Mar 2012 – Mar 2015", "3-Year Historical Growth Journey (Mar 2012 – Mar 2015)", "Scaled from a single-product bootstrap (3.5% CVR) into an omnichannel brand with 40K+ orders, 8.44% peak CVR, and $1.85M+ net revenue.", dt"2012-03-19", dt"2015-03-19"}, {1, "Ch1 Search Launch", "Mar 2012 – Aug 2012", "Bootstrapping on Google Paid Search (Mar 2012 – Aug 2012)", "Single product (Mr. Fuzzy), high desktop dependency, baseline conversion ~3.5%.", dt"2012-03-19", dt"2012-08-31"}, {2, "Ch2 Billing Breakthrough", "Sep 2012 – Dec 2012", "Fixing the Leaky Checkout Bucket (Sep 2012 – Dec 2012)", "Billing-2 A/B test launched, lifting checkout completion from 44.8% to 63.4%.", dt"2012-09-01", dt"2012-12-31"}, {3, "Ch3 Diversification", "Jan 2013 – Jan 2014", "Expanding Search & Introducing Love Bear (Jan 2013 – Jan 2014)", "Bing paid search launched, Love Bear added, conversion crossed 6.6%.", dt"2013-01-01", dt"2014-01-31"}, {4, "Ch4 Cross-Sell Revolution", "Feb 2014 – Dec 2014", "The Hudson Mini Bear Basket Multiplier (Feb 2014 – Dec 2014)", "Mini Bear launched as cross-sell add-on, lifting AOV from $50 to $60 and pushing revenue past $1M.", dt"2014-02-01", dt"2014-12-31"}, {5, "Ch5 Scaled Maturity", "Jan 2015 – Mar 2015", "The Omnichannel High-Conversion Machine (Jan 2015 – Mar 2015)", "Conversion peaks at 8.44%, organic/direct traffic compounds, $1.85M net revenue reached.", dt"2015-01-01", dt"2015-03-19"}})

\tannotation PBI_Id = ab0d9d67-de32-4fdc-b1fe-8bcf8bd64491
'''
param_story_tmdl = f"table _Param_Story\n\tlineageTag: {uid()}\n\n" + "\n".join(param_story_cols) + "\n" + param_story_part


# ==============================================================================
# 18. _Param_CVR_Lift, _Param_Attach, _Param_Refund_Cut
# ==============================================================================
param_cvr_lift_tmdl = f'''table _Param_CVR_Lift
\tlineageTag: {uid()}

\tcolumn Value
\t\tdataType: double
\t\tformatString: 0.00%
\t\tlineageTag: {uid()}
\t\tsummarizeBy: none
\t\tisNameInferred
\t\tsourceColumn: [Value]

\tpartition _Param_CVR_Lift = calculated
\t\tmode: import
\t\tsource = GENERATESERIES(-0.20, 0.50, 0.01)

\tannotation PBI_Id = 41334641-fc8a-4c2c-8ef8-e04f9ffb69eb
'''

param_attach_tmdl = f'''table _Param_Attach
\tlineageTag: {uid()}

\tcolumn Value
\t\tdataType: double
\t\tformatString: 0.00%
\t\tlineageTag: {uid()}
\t\tsummarizeBy: none
\t\tisNameInferred
\t\tsourceColumn: [Value]

\tpartition _Param_Attach = calculated
\t\tmode: import
\t\tsource = GENERATESERIES(0, 0.40, 0.01)

\tannotation PBI_Id = 3c75ab7d-3046-4a4b-9759-9941a8ba539d
'''

param_refund_cut_tmdl = f'''table _Param_Refund_Cut
\tlineageTag: {uid()}

\tcolumn Value
\t\tdataType: double
\t\tformatString: 0.00%
\t\tlineageTag: {uid()}
\t\tsummarizeBy: none
\t\tisNameInferred
\t\tsourceColumn: [Value]

\tpartition _Param_Refund_Cut = calculated
\t\tmode: import
\t\tsource = GENERATESERIES(0, 0.50, 0.01)

\tannotation PBI_Id = 72e41e3d-7d84-48f8-b397-bb7825828453
'''


# ==============================================================================
# 19. _Param_ScenarioPreset (New)
# ==============================================================================
preset_cols = [
    col("PresetID", "int64", is_inferred=True, format_str="0"),
    col("Preset", "string", is_inferred=True),
    col("CVR Lift", "double", is_inferred=True, format_str="0.0%"),
    col("XSell Uplift", "double", is_inferred=True, format_str="0.0%"),
    col("Refund Reduction", "double", is_inferred=True, format_str="0.0%")
]

preset_part = '''\tpartition _Param_ScenarioPreset = calculated
\t\tmode: import
\t\tsource =
\t\t\tDATATABLE(
\t\t\t    "PresetID", INTEGER, "Preset", STRING, "CVR Lift", DOUBLE, "XSell Uplift", DOUBLE, "Refund Reduction", DOUBLE,
\t\t\t    {
\t\t\t        {1, "Conservative", 0.05, 0.03, 0.10},
\t\t\t        {2, "Base", 0.10, 0.08, 0.20},
\t\t\t        {3, "Stretch", 0.20, 0.15, 0.35}
\t\t\t    }
\t\t\t)

\tannotation PBI_Id = c61a0eb1-49b0-4da6-b489-8d76b10fa72c
'''
param_preset_tmdl = f"table _Param_ScenarioPreset\n\tlineageTag: {uid()}\n\n" + "\n".join(preset_cols) + "\n" + preset_part


# ==============================================================================
# 20. _Param_Target
# ==============================================================================
target_cols = [
    col("TargetID", "int64", is_inferred=True, format_str="0"),
    col("TargetName", "string", is_inferred=True),
    col("TargetCVR", "double", is_inferred=True, format_str="0.00%"),
    col("TargetAOV", "double", is_inferred=True, format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00")
]

target_part = '''\tpartition _Param_Target = calculated
\t\tmode: import
\t\tsource =
\t\t\tDATATABLE("TargetID", INTEGER, "TargetName", STRING, "TargetCVR", DOUBLE, "TargetAOV", DOUBLE,
\t\t\t{
\t\t\t    {1, "Company budget", 0.075, 62.0},
\t\t\t    {2, "Prior year", BLANK(), BLANK()},
\t\t\t    {3, "Industry DTC", 0.050, 55.0}
\t\t\t})

\tannotation PBI_Id = 84cae697-30c7-45eb-92c2-809ba8cf2739
'''
param_target_tmdl = f"table _Param_Target\n\tlineageTag: {uid()}\n\n" + "\n".join(target_cols) + "\n" + target_part


# ==============================================================================
# 21. _Param_DateBasis (New)
# ==============================================================================
basis_cols = [
    col("BasisID", "int64", is_inferred=True, format_str="0"),
    col("Basis", "string", is_inferred=True)
]

basis_part = '''\tpartition _Param_DateBasis = calculated
\t\tmode: import
\t\tsource = DATATABLE("BasisID", INTEGER, "Basis", STRING, { {1, "Order date (cohort)"}, {2, "Refund date (cash)"} })

\tannotation PBI_Id = c1e83120-d09f-43fb-8ea8-37c02b9e6f21
'''
param_basis_tmdl = f"table _Param_DateBasis\n\tlineageTag: {uid()}\n\n" + "\n".join(basis_cols) + "\n" + basis_part


# ==============================================================================
# 22. Basket_Pairs, _Param_LanderA, _Param_LanderB, _Param_CohortAge (Preserved)
# ==============================================================================
basket_pairs_tmdl = f'''table Basket_Pairs
\tlineageTag: {uid()}

{col("order_item_id", "int64", is_inferred=True, format_str="0")}
{col("created_at", "dateTime", is_inferred=True, format_str="General Date")}
{col("order_id", "int64", is_inferred=True, format_str="0")}
{col("product_id", "int64", is_inferred=True, format_str="0")}
{col("is_primary_item", "int64", is_inferred=True, format_str="0")}
{col("price_usd", "double", is_inferred=True, format_str=r"\\$#,0.00;(\\S#,0.00);\\$#,0.00")}
{col("cogs_usd", "double", is_inferred=True, format_str=r"\\$#,0.00;(\\S#,0.00);\\$#,0.00")}
{col("PrimaryProductID", "int64", is_inferred=True, format_str="0")}
{col("CrossProductID", "int64", is_inferred=True, format_str="0")}

\tpartition Basket_Pairs = calculated
\t\tmode: import
\t\tsource = ADDCOLUMNS(FILTER(order_items, order_items[is_primary_item] = 0), "PrimaryProductID", LOOKUPVALUE(orders[primary_product_id], orders[order_id], [order_id]), "CrossProductID", [product_id])

\tannotation PBI_Id = {uid()}
'''

param_landera_tmdl = f'''table _Param_LanderA
\tlineageTag: {uid()}

{col("LanderA", "string", is_inferred=True)}
{col("SortOrder", "int64", is_inferred=True, format_str="0")}

\tpartition _Param_LanderA = calculated
\t\tmode: import
\t\tsource = DATATABLE("LanderA", STRING, "SortOrder", INTEGER, {{{{"/home", 1}}, {{"/lander-1", 2}}, {{"/lander-2", 3}}, {{"/lander-3", 4}}, {{"/lander-4", 5}}, {{"/lander-5", 6}}}})

\tannotation PBI_Id = {uid()}
'''

param_landerb_tmdl = f'''table _Param_LanderB
\tlineageTag: {uid()}

{col("LanderB", "string", is_inferred=True)}
{col("SortOrder", "int64", is_inferred=True, format_str="0")}

\tpartition _Param_LanderB = calculated
\t\tmode: import
\t\tsource = DATATABLE("LanderB", STRING, "SortOrder", INTEGER, {{{{"/home", 1}}, {{"/lander-1", 2}}, {{"/lander-2", 3}}, {{"/lander-4", 4}}, {{"/lander-5", 5}}}})

\tannotation PBI_Id = {uid()}
'''

param_cohort_age_tmdl = f'''table _Param_CohortAge
\tlineageTag: {uid()}

{col("Value", "int64", is_inferred=True, format_str="0")}

\tpartition _Param_CohortAge = calculated
\t\tmode: import
\t\tsource = GENERATESERIES(0, 12, 1)

\tannotation PBI_Id = {uid()}
'''


# ==============================================================================
# 23. _Measures (Complete DAX Catalog with 7 Display Folders)
# ==============================================================================
def measure(name, dax, folder, format_str=None, dyn_format=None):
    clean_dax = " ".join(line.strip() for line in dax.strip().splitlines() if line.strip())
    lines = [f"\tmeasure '{name}' = {clean_dax}"]
    if format_str:
        lines.append(f"\t\tformatString: {format_str}")
    lines.append(f"\t\tdisplayFolder: {folder}")
    lines.append(f"\t\tlineageTag: {uid()}")
    if dyn_format:
        clean_dyn = " ".join(line.strip() for line in dyn_format.strip().splitlines() if line.strip())
        lines.append(f"\t\tformatStringDefinition =\n\t\t\t{clean_dyn}")
    lines.append("")
    return "\n".join(lines)

meas_list = [
    # 01 Volume
    measure("Total Sessions", "COUNTROWS(website_sessions)", "01 Volume", format_str="#,0"),
    measure("Total Orders", "COUNTROWS(orders)", "01 Volume", format_str="#,0"),
    measure("Units Sold", "COUNTROWS(order_items)", "01 Volume", format_str="#,0"),
    measure("Unpaid Session %", 'DIVIDE(CALCULATE([Total Sessions], website_sessions[Traffic Type] <> "Paid"), [Total Sessions], 0)', "01 Volume", format_str="0.00%"),
    measure("Mobile Traffic %", 'DIVIDE(CALCULATE([Total Sessions], website_sessions[device_type] = "mobile"), [Total Sessions], 0)', "01 Volume", format_str="0.00%"),

    # 02 Financial
    measure("Gross Revenue", "SUM(order_items[price_usd])", "02 Financial", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    measure("Total COGS", "SUM(order_items[cogs_usd])", "02 Financial", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    measure("Gross Profit", "[Gross Revenue] - [Total COGS]", "02 Financial", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    measure("Gross Margin %", "DIVIDE([Gross Profit], [Gross Revenue], 0)", "02 Financial", format_str="0.00%"),
    measure("Total Refund Amount", "SUM(order_item_refunds[refund_amount_usd])", "02 Financial", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    measure("Net Revenue", "[Gross Revenue] - [Total Refund Amount]", "02 Financial", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    measure("Net Profit", "[Gross Profit] - [Total Refund Amount]", "02 Financial", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    measure("Net Margin %", "DIVIDE([Net Profit], [Net Revenue], 0)", "02 Financial", format_str="0.00%"),
    measure("Average Order Value", "DIVIDE([Gross Revenue], [Total Orders], 0)", "02 Financial", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    measure("Revenue per Session", "DIVIDE([Gross Revenue], [Total Sessions], 0)", "02 Financial", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    measure("Unpaid Revenue", 'CALCULATE([Gross Revenue], website_sessions[Traffic Type] <> "Paid")', "02 Financial", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    measure("Avg Refund Lag Days", "AVERAGE(order_item_refunds[Refund Lag Days])", "02 Financial", format_str="0.0"),
    measure("Refund $ (Basis)", "IF(SELECTEDVALUE(_Param_DateBasis[BasisID], 1) = 1, CALCULATE([Total Refund Amount], USERELATIONSHIP(Dim_Date[Date], order_item_refunds[Order Date])), [Total Refund Amount])", "02 Financial", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    measure("Refund Rate %", "DIVIDE([Total Refund Amount], [Gross Revenue], 0)", "02 Financial", format_str="0.00%"),

    # 03 Funnel and CRO
    measure("Bounced Sessions", "CALCULATE([Total Sessions], website_sessions[Is Bounce] = 1)", "03 Funnel and CRO", format_str="#,0"),
    measure("Bounce Rate %", "DIVIDE([Bounced Sessions], [Total Sessions], 0)", "03 Funnel and CRO", format_str="0.00%"),
    measure("Conversion Rate %", "DIVIDE([Total Orders], [Total Sessions], 0)", "03 Funnel and CRO", format_str="0.00%"),
    measure("CVR Desktop", 'CALCULATE([Conversion Rate %], website_sessions[device_type] = "desktop")', "03 Funnel and CRO", format_str="0.00%"),
    measure("CVR Mobile", 'CALCULATE([Conversion Rate %], website_sessions[device_type] = "mobile")', "03 Funnel and CRO", format_str="0.00%"),
    measure("Best Lander CVR", "MAXX(ALL(Dim_Lander[Landing Page]), [Conversion Rate %])", "03 Funnel and CRO", format_str="0.00%"),
    measure("Lowest Bounce %", "MINX(ALL(Dim_Lander[Landing Page]), [Bounce Rate %])", "03 Funnel and CRO", format_str="0.00%"),
    measure("Billing Conversion %", "DIVIDE(CALCULATE([Total Orders], NOT(ISBLANK(website_sessions[Billing Variant]))), CALCULATE([Total Sessions], NOT(ISBLANK(website_sessions[Billing Variant]))), 0)", "03 Funnel and CRO", format_str="0.00%"),
    measure("Billing Lift pp", 'CALCULATE([Conversion Rate %], website_sessions[Billing Variant] = "billing-2") - CALCULATE([Conversion Rate %], website_sessions[Billing Variant] = "billing")', "03 Funnel and CRO", format_str="+0.00%;-0.00%;0.00%"),
    measure("Billing Z-Score", '''VAR n1 = CALCULATE([Total Sessions], website_sessions[Billing Variant] = "billing")
VAR n2 = CALCULATE([Total Sessions], website_sessions[Billing Variant] = "billing-2")
VAR x1 = CALCULATE([Total Orders],   website_sessions[Billing Variant] = "billing")
VAR x2 = CALCULATE([Total Orders],   website_sessions[Billing Variant] = "billing-2")
VAR p1 = DIVIDE(x1, n1)  VAR p2 = DIVIDE(x2, n2)  VAR p = DIVIDE(x1 + x2, n1 + n2)
VAR se = SQRT(p * (1 - p) * (DIVIDE(1, n1) + DIVIDE(1, n2)))
RETURN DIVIDE(p2 - p1, se)''', "03 Funnel and CRO", format_str="0.0"),
    measure("Checkout Completion %", "DIVIDE([Total Orders], CALCULATE([Total Sessions], website_sessions[Funnel Depth] >= 6), 0)", "03 Funnel and CRO", format_str="0.00%"),
    measure("Funnel Sessions", "VAR s = COALESCE(SELECTEDVALUE(_Dim_FunnelStep[StepID]), SELECTEDVALUE(_Dim_FunnelStep[StepNumber]), 1) RETURN CALCULATE(COUNTROWS(website_sessions), website_sessions[Funnel Depth] >= s)", "03 Funnel and CRO", format_str="#,0"),
    measure("Step Conversion %", "VAR s = COALESCE(SELECTEDVALUE(_Dim_FunnelStep[StepID]), SELECTEDVALUE(_Dim_FunnelStep[StepNumber]), 1) VAR prev = CALCULATE(COUNTROWS(website_sessions), website_sessions[Funnel Depth] >= s - 1) RETURN IF(s = 1, 1, DIVIDE([Funnel Sessions], prev, 0))", "03 Funnel and CRO", format_str="0.00%"),
    measure("Verdict HTML", 'VAR z = [Billing Z-Score] VAR lift = [Billing Lift pp] RETURN "<div style=\'font-family:Segoe UI;color:#e6e9f2\'><div style=\'font-size:32px;font-weight:800;color:#34d399\'>+" & FORMAT(lift * 100, "0.00") & " pp</div><div style=\'font-size:12px\'>z = " & FORMAT(z, "0.0") & " - " & IF(ABS(z) >= 1.96, "significant at 95%", "not significant") & "</div></div>"', "03 Funnel and CRO"),

    # 04 Product
    measure("Primary Units", "CALCULATE(COUNTROWS(order_items), order_items[is_primary_item] = 1)", "04 Product", format_str="#,0"),
    measure("Cross-Sell Units", "CALCULATE(COUNTROWS(order_items), order_items[is_primary_item] = 0)", "04 Product", format_str="#,0"),
    measure("Cross-Sell Attach Rate %", "DIVIDE([Cross-Sell Units], [Total Orders], 0)", "04 Product", format_str="0.00%"),
    measure("Mini Bear Cross-Sell Share", "DIVIDE(CALCULATE([Cross-Sell Units], order_items[product_id] = 4), CALCULATE(COUNTROWS(order_items), order_items[product_id] = 4), 0)", "04 Product", format_str="0.00%"),
    measure("Primary AOV", "DIVIDE(CALCULATE(SUM(order_items[price_usd]), order_items[is_primary_item] = 1), [Total Orders], 0)", "04 Product", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    measure("Cross-Sell AOV Contribution", "DIVIDE(CALCULATE(SUM(order_items[price_usd]), order_items[is_primary_item] = 0), [Total Orders], 0)", "04 Product", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    measure("Product Refund Rate %", "DIVIDE(COUNTROWS(order_item_refunds), COUNTROWS(order_items), 0)", "04 Product", format_str="0.00%"),
    measure("Best Margin Product", "MAXX(TOPN(1, ALL(products), [Unit Margin %], DESC), products[product_name])", "04 Product"),

    # 05 Retention
    measure("Repeat Sessions", "CALCULATE([Total Sessions], website_sessions[is_repeat_session] = 1)", "05 Retention", format_str="#,0"),
    measure("Repeat Session %", "DIVIDE([Repeat Sessions], [Total Sessions], 0)", "05 Retention", format_str="0.00%"),
    measure("CVR Repeat", "CALCULATE([Conversion Rate %], website_sessions[is_repeat_session] = 1)", "05 Retention", format_str="0.00%"),
    measure("CVR New", "CALCULATE([Conversion Rate %], website_sessions[is_repeat_session] = 0)", "05 Retention", format_str="0.00%"),
    measure("Repeat Orders", "CALCULATE([Total Orders], orders[Is Repeat Order] = 1)", "05 Retention", format_str="#,0"),
    measure("Repeat Revenue", "CALCULATE([Gross Revenue], orders[Is Repeat Order] = 1)", "05 Retention", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    measure("One-time Buyer %", "DIVIDE(CALCULATE(DISTINCTCOUNT(orders[user_id]), orders[Order Seq] = 1, orders[Is Repeat Order] = 0), DISTINCTCOUNT(orders[user_id]), 0)", "05 Retention", format_str="0.00%"),
    measure("Repeat Buyer %", "DIVIDE(CALCULATE(DISTINCTCOUNT(orders[user_id]), orders[Is Repeat Order] = 1), DISTINCTCOUNT(orders[user_id]), 0)", "05 Retention", format_str="0.00%"),
    measure("Repeat Order Rate", "DIVIDE([Repeat Orders], [Total Orders], 0)", "05 Retention", format_str="0.00%"),
    measure("Retention Callout HTML", '''"<div style='font-family:Segoe UI;color:#e6e9f2'>"
 & "<div style='font-size:32px;font-weight:800;color:#fb7185'>98.1%</div>"
 & "<div style='font-size:12px;color:#b5c0dc'>of buyers never came back. Repeat sessions convert 18% better, yet only 591 of 31,696 buyers ordered again.</div></div>"''', "05 Retention"),

    # 06 Dynamic
    measure("Dynamic Selected Metric", '''SWITCH(SELECTEDVALUE(_Param_Metric[MetricID], 1),
  1, [Gross Revenue], 2, [Net Revenue], 3, [Gross Profit], 4, [Gross Margin %], 5, [Total Orders],
  6, [Total Sessions], 7, [Conversion Rate %], 8, [Average Order Value], 9, [Cross-Sell Attach Rate %],
  10, [Refund Rate %], [Gross Revenue])''', "06 Dynamic", dyn_format='''SWITCH(SELECTEDVALUE(_Param_Metric[MetricID], 1),
  1, "\\$#,0.00", 2, "\\$#,0.00", 3, "\\$#,0.00", 4, "0.00%", 5, "#,0",
  6, "#,0", 7, "0.00%", 8, "\\$#,0.00", 9, "0.00%", 10, "0.00%", "\\$#,0.00")'''),
    measure("Time Mode Value", '''VAR m   = SELECTEDVALUE(_Param_Time[TimeModeID], 1)
VAR cur = [Dynamic Selected Metric]
VAR pp  = CALCULATE([Dynamic Selected Metric], DATEADD(Dim_Date[Date], -1, MONTH))
VAR py  = CALCULATE([Dynamic Selected Metric], SAMEPERIODLASTYEAR(Dim_Date[Date]))
VAR r30 = CALCULATE([Dynamic Selected Metric], DATESINPERIOD(Dim_Date[Date], MAX(Dim_Date[Date]), -30, DAY))
RETURN SWITCH(m, 1, cur, 2, pp, 3, py, 4, cur - py, 5, DIVIDE(cur - py, py), r30)''', "06 Dynamic"),
    measure("Dyn Axis Metric", '''VAR d = SELECTEDVALUE(_Param_Dim[DimID], 1)
VAR members = VALUES(_Param_Dim[Member])
RETURN SWITCH(d,
  1, CALCULATE([Dynamic Selected Metric], TREATAS(members, Dim_Channel[Channel Grouping])),
  2, CALCULATE([Dynamic Selected Metric], TREATAS(members, website_sessions[device_type])),
  3, CALCULATE([Dynamic Selected Metric], TREATAS(members, products[product_name])),
  4, CALCULATE([Dynamic Selected Metric], TREATAS(members, Dim_Lander[Landing Page])),
  5, CALCULATE([Dynamic Selected Metric], TREATAS(members, Dim_Channel[Campaign Type]))
)''', "06 Dynamic"),
    measure("Story Headline Text", 'SELECTEDVALUE(_Param_Story[Headline], "3-Year Historical Growth Journey (Mar 2012 – Mar 2015)")', "06 Dynamic"),
    measure("Story Narrative Commentary", 'SELECTEDVALUE(_Param_Story[Commentary], "Scaled from a single-product bootstrap (3.5% CVR) into an omnichannel brand with 40K+ orders, 8.44% peak CVR, and $1.85M+ net revenue.")', "06 Dynamic"),
    measure("Story Narrative HTML", '''VAR Eyebrow =
    VAR ch = SELECTEDVALUE(_Param_Story[ChapterName], "All 3 Years")
    RETURN IF(ch = "All 3 Years" || ISBLANK(ch), "MAVEN FUZZY FACTORY", UPPER(ch))
VAR Headline =
    SELECTEDVALUE(_Param_Story[Headline], "3-Year Historical Growth Journey (Mar 2012 – Mar 2015)")
VAR Commentary =
    SELECTEDVALUE(_Param_Story[Commentary], "Scaled from a single-product bootstrap (3.5% CVR) into an omnichannel brand with 40K+ orders, 8.44% peak CVR, and $1.85M+ net revenue.")
RETURN
    "<style>html, body { margin:0; padding:0; width:100%; height:100%; overflow:hidden; background:transparent; font-family:'Segoe UI', -apple-system, sans-serif; }</style>" &
    "<div style='display: flex; flex-direction: column; justify-content: center; height: 100%; box-sizing: border-box; padding: 6px 10px;'>" &
        "<div style='font-size: 10px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: #2DD4BF; margin-bottom: 4px;'>" &
            Eyebrow &
        "</div>" &
        "<div style='font-size: 18px; font-weight: 700; line-height: 1.25; color: #FFFFFF; margin-bottom: 6px;'>" &
            Headline &
        "</div>" &
        "<div style='font-size: 12px; line-height: 1.45; color: #B5C0DC;'>" &
            Commentary &
        "</div>" &
    "</div>"''', "06 Dynamic"),
    measure("Orders (Chapter)", '''VAR s = SELECTEDVALUE(_Param_Story[StartDate], DATE(2012,3,19))
VAR e = SELECTEDVALUE(_Param_Story[EndDate],   DATE(2015,3,19))
RETURN CALCULATE([Total Orders], DATESBETWEEN(Dim_Date[Date], s, e))''', "06 Dynamic", format_str="#,0"),
    measure("Sessions (Chapter)", '''VAR s = SELECTEDVALUE(_Param_Story[StartDate], DATE(2012,3,19))
VAR e = SELECTEDVALUE(_Param_Story[EndDate],   DATE(2015,3,19))
RETURN CALCULATE([Total Sessions], DATESBETWEEN(Dim_Date[Date], s, e))''', "06 Dynamic", format_str="#,0"),
    measure("Conversion Rate % (Chapter)", '''VAR s = SELECTEDVALUE(_Param_Story[StartDate], DATE(2012,3,19))
VAR e = SELECTEDVALUE(_Param_Story[EndDate],   DATE(2015,3,19))
RETURN CALCULATE([Conversion Rate %], DATESBETWEEN(Dim_Date[Date], s, e))''', "06 Dynamic", format_str="0.00%"),
    measure("AOV (Chapter)", '''VAR s = SELECTEDVALUE(_Param_Story[StartDate], DATE(2012,3,19))
VAR e = SELECTEDVALUE(_Param_Story[EndDate],   DATE(2015,3,19))
RETURN CALCULATE([Average Order Value], DATESBETWEEN(Dim_Date[Date], s, e))''', "06 Dynamic", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    measure("Gross Margin % (Chapter)", '''VAR s = SELECTEDVALUE(_Param_Story[StartDate], DATE(2012,3,19))
VAR e = SELECTEDVALUE(_Param_Story[EndDate],   DATE(2015,3,19))
RETURN CALCULATE([Gross Margin %], DATESBETWEEN(Dim_Date[Date], s, e))''', "06 Dynamic", format_str="0.00%"),
    measure("KPI Strip HTML", '''VAR s = SELECTEDVALUE(_Param_Story[StartDate], DATE(2012, 3, 19))
VAR e = SELECTEDVALUE(_Param_Story[EndDate], DATE(2015, 3, 19))
VAR ch = SELECTEDVALUE(_Param_Story[ChapterName], "All 3 Years")
VAR isAll = (ch = "All 3 Years" || ISBLANK(ch))
VAR rev = CALCULATE([Gross Revenue], DATESBETWEEN(Dim_Date[Date], s, e))
VAR ord = CALCULATE([Total Orders], DATESBETWEEN(Dim_Date[Date], s, e))
VAR sess = CALCULATE([Total Sessions], DATESBETWEEN(Dim_Date[Date], s, e))
VAR cvr = DIVIDE(ord, sess, 0)
VAR aov = DIVIDE(rev, ord, 0)
VAR cogs = CALCULATE([Total COGS], DATESBETWEEN(Dim_Date[Date], s, e))
VAR gm = DIVIDE(rev - cogs, rev, 0)
VAR revStr = IF(rev >= 1000000, "$" & FORMAT(rev / 1000000, "0.00") & "M", IF(rev >= 1000, "$" & FORMAT(rev / 1000, "0.0") & "K", "$" & FORMAT(rev, "#,0")))
VAR ordStr = IF(ord >= 1000, FORMAT(ord / 1000, "0.0") & "K", FORMAT(ord, "#,0"))
VAR sessStr = IF(sess >= 1000000, FORMAT(sess / 1000000, "0.00") & "M", IF(sess >= 1000, FORMAT(sess / 1000, "0.0") & "K", FORMAT(sess, "#,0")))
VAR cvrStr = FORMAT(cvr, "0.00%")
VAR aovStr = FORMAT(aov, "$0.00")
VAR gmStr = FORMAT(gm, "0.0%")
VAR subRev = IF(isAll, "3-Year Gross", "Chapter Total")
VAR subOrd = IF(isAll, "Total Converted", "Chapter Orders")
VAR subSess = IF(isAll, "Omnichannel Visits", "Traffic Visits")
VAR subCvr = IF(isAll, "Blended CVR", "Chapter CVR")
VAR subAov = IF(isAll, "Basket Avg", "Order Basket")
VAR subGm = IF(isAll, "Net Margin %", "Chapter Margin")
RETURN
    "<style>" &
    "html, body { margin:0; padding:0; width:100%; height:100%; overflow:hidden; background:transparent; font-family:'Segoe UI', -apple-system, sans-serif; }" &
    ".kpi-grid { display:grid; grid-template-columns:repeat(6, 1fr); gap:8px; width:100%; height:100%; box-sizing:border-box; padding:1px 0; }" &
    ".kpi-card { background:#0F1730; border:1px solid #1D2749; border-radius:8px; padding:10px 12px; display:flex; flex-direction:column; justify-content:space-between; height:100%; box-sizing:border-box; min-width:0; transition:all 0.2s ease; }" &
    ".kpi-card:hover { background:#131E3D; border-color:#2DD4BF; box-shadow:0 4px 12px rgba(0,0,0,0.25); }" &
    ".kpi-label { font-size:10px; color:#8B95B0; font-weight:600; text-transform:uppercase; letter-spacing:0.6px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; line-height:1.2; }" &
    ".kpi-value { font-size:24px; font-weight:700; line-height:1.15; letter-spacing:-0.5px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; margin:2px 0; }" &
    ".kpi-sub { font-size:9.5px; color:#64748B; font-weight:500; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; line-height:1.2; }" &
    "</style>" &
    "<div class='kpi-grid' style='display:grid; grid-template-columns:repeat(6, 1fr); gap:8px; width:100%; height:100%; box-sizing:border-box; padding:1px 0;'>" &
        "<div class='kpi-card' style='background:#0F1730; border:1px solid #1D2749; border-radius:8px; padding:10px 12px; display:flex; flex-direction:column; justify-content:space-between; height:100%; box-sizing:border-box;'>" &
            "<div class='kpi-label' style='font-size:10px; color:#8B95B0; font-weight:600; text-transform:uppercase; letter-spacing:0.6px;'>Gross Revenue</div>" &
            "<div class='kpi-value' style='font-size:24px; font-weight:700; color:#38BDF8;'>" & revStr & "</div>" &
            "<div class='kpi-sub' style='font-size:9.5px; color:#64748B; font-weight:500;'>" & subRev & "</div>" &
        "</div>" &
        "<div class='kpi-card' style='background:#0F1730; border:1px solid #1D2749; border-radius:8px; padding:10px 12px; display:flex; flex-direction:column; justify-content:space-between; height:100%; box-sizing:border-box;'>" &
            "<div class='kpi-label' style='font-size:10px; color:#8B95B0; font-weight:600; text-transform:uppercase; letter-spacing:0.6px;'>Orders</div>" &
            "<div class='kpi-value' style='font-size:24px; font-weight:700; color:#34D399;'>" & ordStr & "</div>" &
            "<div class='kpi-sub' style='font-size:9.5px; color:#64748B; font-weight:500;'>" & subOrd & "</div>" &
        "</div>" &
        "<div class='kpi-card' style='background:#0F1730; border:1px solid #1D2749; border-radius:8px; padding:10px 12px; display:flex; flex-direction:column; justify-content:space-between; height:100%; box-sizing:border-box;'>" &
            "<div class='kpi-label' style='font-size:10px; color:#8B95B0; font-weight:600; text-transform:uppercase; letter-spacing:0.6px;'>Sessions</div>" &
            "<div class='kpi-value' style='font-size:24px; font-weight:700; color:#22D3EE;'>" & sessStr & "</div>" &
            "<div class='kpi-sub' style='font-size:9.5px; color:#64748B; font-weight:500;'>" & subSess & "</div>" &
        "</div>" &
        "<div class='kpi-card' style='background:#0F1730; border:1px solid #1D2749; border-radius:8px; padding:10px 12px; display:flex; flex-direction:column; justify-content:space-between; height:100%; box-sizing:border-box;'>" &
            "<div class='kpi-label' style='font-size:10px; color:#8B95B0; font-weight:600; text-transform:uppercase; letter-spacing:0.6px;'>CVR</div>" &
            "<div class='kpi-value' style='font-size:24px; font-weight:700; color:#FBBF24;'>" & cvrStr & "</div>" &
            "<div class='kpi-sub' style='font-size:9.5px; color:#64748B; font-weight:500;'>" & subCvr & "</div>" &
        "</div>" &
        "<div class='kpi-card' style='background:#0F1730; border:1px solid #1D2749; border-radius:8px; padding:10px 12px; display:flex; flex-direction:column; justify-content:space-between; height:100%; box-sizing:border-box;'>" &
            "<div class='kpi-label' style='font-size:10px; color:#8B95B0; font-weight:600; text-transform:uppercase; letter-spacing:0.6px;'>AOV</div>" &
            "<div class='kpi-value' style='font-size:24px; font-weight:700; color:#A78BFA;'>" & aovStr & "</div>" &
            "<div class='kpi-sub' style='font-size:9.5px; color:#64748B; font-weight:500;'>" & subAov & "</div>" &
        "</div>" &
        "<div class='kpi-card' style='background:#0F1730; border:1px solid #1D2749; border-radius:8px; padding:10px 12px; display:flex; flex-direction:column; justify-content:space-between; height:100%; box-sizing:border-box;'>" &
            "<div class='kpi-label' style='font-size:10px; color:#8B95B0; font-weight:600; text-transform:uppercase; letter-spacing:0.6px;'>Gross Margin</div>" &
            "<div class='kpi-value' style='font-size:24px; font-weight:700; color:#2DD4BF;'>" & gmStr & "</div>" &
            "<div class='kpi-sub' style='font-size:9.5px; color:#64748B; font-weight:500;'>" & subGm & "</div>" &
        "</div>" &
    "</div>"''', "06 Dynamic"),
    measure("Revenue (Chapter)", '''VAR s = SELECTEDVALUE(_Param_Story[StartDate], DATE(2012,3,19))
VAR e = SELECTEDVALUE(_Param_Story[EndDate],   DATE(2015,3,19))
RETURN CALCULATE([Gross Revenue], DATESBETWEEN(Dim_Date[Date], s, e))''', "06 Dynamic", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    measure("Is Selected Chapter", '''VAR id = SELECTEDVALUE(_Param_Story[ChapterID], 0)
RETURN IF(id = 0 || SELECTEDVALUE(Dim_Date[Chapter ID]) = id, 1, 0)''', "06 Dynamic", format_str="0"),
    measure("CVR Target", '''VAR m = SELECTEDVALUE(_Param_Target[TargetID], 1)
RETURN IF(m = 2, CALCULATE([Conversion Rate %], SAMEPERIODLASTYEAR(Dim_Date[Date])), SELECTEDVALUE(_Param_Target[TargetCVR]))''', "06 Dynamic", format_str="0.00%"),
    measure("Page Title P1", '"Maven Fuzzy Factory · " & SELECTEDVALUE(_Param_Story[ChapterName], "The 3-Year Growth Story") & " · " & SELECTEDVALUE(_Param_Metric[MetricName], "Gross Revenue ($)")', "06 Dynamic"),
    measure("Page Title P2", '"Acquisition · " & IF(ISFILTERED(Dim_Date[Year]), SELECTEDVALUE(Dim_Date[Year], "multi-year"), "2012–2015") & " · grouped by " & SELECTEDVALUE(_Param_Dim[DimName], "Marketing Channel")', "06 Dynamic"),
    measure("Page Title P3", '"CRO Lab · " & FORMAT([Conversion Rate %], "0.00%") & " blended CVR · best lander " & MAXX(TOPN(1, ALL(Dim_Lander[Landing Page]), [Conversion Rate %]), Dim_Lander[Landing Page])', "06 Dynamic"),
    measure("Page Title P4", '"Portfolio · " & FORMAT([Cross-Sell Attach Rate %], "0.0%") & " attach rate · AOV " & FORMAT([Average Order Value], "$0.00")', "06 Dynamic"),
    measure("Page Title P5", '"Retention · repeat sessions convert " & FORMAT(DIVIDE([CVR Repeat], [CVR New]) - 1, "+0%") & " better, only " & FORMAT([Repeat Buyer %], "0.0%") & " of buyers reorder"', "06 Dynamic"),
    measure("Page Title P6", '"Financial health · net margin " & FORMAT([Net Margin %], "0.0%") & " · refunds " & FORMAT([Total Refund Amount], "$#,0") & " by " & IF(SELECTEDVALUE(_Param_DateBasis[BasisID], 1) = 1, "order date", "refund date")', "06 Dynamic"),
    measure("Page Title P7", '"What-if · " & FORMAT([Scn Net Revenue] - [Net Revenue], "+$#,0;-$#,0") & " net revenue vs baseline"', "06 Dynamic"),

    # 07 Scenario
    measure("CVR Lift Value", "IF(ISFILTERED(_Param_ScenarioPreset[Preset]), SELECTEDVALUE(_Param_ScenarioPreset[CVR Lift]), SELECTEDVALUE(_Param_CVR_Lift[Value], 0))", "07 Scenario", format_str="0.00%"),
    measure("XSell Uplift", "IF(ISFILTERED(_Param_ScenarioPreset[Preset]), SELECTEDVALUE(_Param_ScenarioPreset[XSell Uplift]), SELECTEDVALUE(_Param_Attach[Value], 0))", "07 Scenario", format_str="0.00%"),
    measure("Refund Reduction", "IF(ISFILTERED(_Param_ScenarioPreset[Preset]), SELECTEDVALUE(_Param_ScenarioPreset[Refund Reduction]), SELECTEDVALUE(_Param_Refund_Cut[Value], 0))", "07 Scenario", format_str="0.00%"),
    measure("Avg Cross-Sell Price", "DIVIDE(CALCULATE(SUM(order_items[price_usd]), order_items[is_primary_item] = 0), [Cross-Sell Units], 0)", "07 Scenario", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    measure("Refund Rate $", "DIVIDE([Total Refund Amount], [Gross Revenue], 0)", "07 Scenario", format_str="0.00%"),
    measure("Scn Orders", "[Total Orders] * (1 + [CVR Lift Value])", "07 Scenario", format_str="#,0"),
    measure("Scn CVR Revenue", "[Total Orders] * [CVR Lift Value] * [Average Order Value]", "07 Scenario", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    measure("Scn Cross-Sell Revenue", "[Scn Orders] * [XSell Uplift] * [Avg Cross-Sell Price]", "07 Scenario", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    measure("Scn Incr Refunds", "([Scn CVR Revenue] + [Scn Cross-Sell Revenue]) * [Refund Rate $]", "07 Scenario", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    measure("Scn Refund Savings", "([Total Refund Amount] + [Scn Incr Refunds]) * [Refund Reduction]", "07 Scenario", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    measure("Scn Net Revenue", "[Net Revenue] + [Scn CVR Revenue] + [Scn Cross-Sell Revenue] - [Scn Incr Refunds] + [Scn Refund Savings]", "07 Scenario", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    measure("Scn Net Revenue Delta", "[Scn Net Revenue] - [Net Revenue]", "07 Scenario", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    measure("Scn Net Profit", "[Scn Net Revenue] - [Total COGS] * DIVIDE([Scn Orders], [Total Orders], 1)", "07 Scenario", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    measure("Scn CVR", "DIVIDE([Scn Orders], [Total Sessions], 0)", "07 Scenario", format_str="0.00%")
]

measures_tmdl = f'''table _Measures
\tlineageTag: {uid()}

''' + "\n".join(meas_list) + f'''\tcolumn Dummy
\t\tdataType: int64
\t\tisHidden
\t\tformatString: 0
\t\tlineageTag: {uid()}
\t\tsummarizeBy: none
\t\tisNameInferred
\t\tsourceColumn: [Dummy]

\tpartition _Measures = calculated
\t\tmode: import
\t\tsource = ROW("Dummy", 1)

\tannotation PBI_Id = {uid()}
'''


# ==============================================================================
# Write all tables to disk
# ==============================================================================
tables_map = {
    "website_pageviews": website_pageviews_tmdl,
    "website_sessions": website_sessions_tmdl,
    "orders": orders_tmdl,
    "order_items": order_items_tmdl,
    "order_item_refunds": order_item_refunds_tmdl,
    "products": products_tmdl,
    "Dim_PrimaryProduct": dim_primary_product_tmdl,
    "Dim_Date": dim_date_tmdl,
    "Dim_Channel": dim_channel_tmdl,
    "Dim_Lander": dim_lander_tmdl,
    "Dim_Customer": dim_customer_tmdl,
    "Sens_Grid": sens_grid_tmdl,
    "_Dim_FunnelStep": dim_funnel_step_tmdl,
    "_Param_Metric": param_metric_tmdl,
    "_Param_Time": param_time_tmdl,
    "_Param_Dim": param_dim_tmdl,
    "_Param_Story": param_story_tmdl,
    "_Param_CVR_Lift": param_cvr_lift_tmdl,
    "_Param_Attach": param_attach_tmdl,
    "_Param_Refund_Cut": param_refund_cut_tmdl,
    "_Param_ScenarioPreset": param_preset_tmdl,
    "_Param_Target": param_target_tmdl,
    "_Param_DateBasis": param_basis_tmdl,
    "Basket_Pairs": basket_pairs_tmdl,
    "_Param_LanderA": param_landera_tmdl,
    "_Param_LanderB": param_landerb_tmdl,
    "_Param_CohortAge": param_cohort_age_tmdl,
    "_Measures": measures_tmdl
}

for name, content in tables_map.items():
    p = os.path.join(tables_dir, f"{name}.tmdl")
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    print("Wrote:", f"{name}.tmdl")


# ==============================================================================
# STEP 5: definition/relationships.tmdl
# ==============================================================================
relationships_list = [
    # 1. Dim_Date[Date] -> website_sessions[Session Date] (Active, 1:*)
    ("website_sessions.'Session Date'", "Dim_Date.Date", True),
    # 2. Dim_Date[Date] -> orders[Order Date] (Active, 1:*)
    ("orders.'Order Date'", "Dim_Date.Date", True),
    # 3. Dim_Date[Date] -> order_items[Order Date] (Active, 1:*)
    ("order_items.'Order Date'", "Dim_Date.Date", True),
    # 4. Dim_Date[Date] -> order_item_refunds[Refund Date] (Active, 1:*)
    ("order_item_refunds.'Refund Date'", "Dim_Date.Date", True),
    # 5. Dim_Date[Date] -> order_item_refunds[Order Date] (Inactive, 1:*)
    ("order_item_refunds.'Order Date'", "Dim_Date.Date", False),
    # 6. Dim_Channel[Channel Grouping] -> website_sessions[Channel Grouping] (Active, 1:*)
    ("website_sessions.'Channel Grouping'", "Dim_Channel.'Channel Grouping'", True),
    # 7. Dim_Lander[Landing Page] -> website_sessions[Landing Page] (Active, 1:*)
    ("website_sessions.'Landing Page'", "Dim_Lander.'Landing Page'", True),
    # 8. Dim_Customer[user_id] -> website_sessions[user_id] (Active, 1:*)
    ("website_sessions.user_id", "Dim_Customer.user_id", True),
    # 9. website_sessions[website_session_id] -> website_pageviews[website_session_id] (Active, 1:*)
    ("website_pageviews.website_session_id", "website_sessions.website_session_id", True),
    # 10. website_sessions[website_session_id] -> orders[website_session_id] (Active, 1:1 single direction from sessions to orders)
    ("orders.website_session_id", "website_sessions.website_session_id", True),
    # 11. orders[order_id] -> order_items[order_id] (Active, 1:*)
    ("order_items.order_id", "orders.order_id", True),
    # 12. order_items[order_item_id] -> order_item_refunds[order_item_id] (Active, 1:1 single direction from items to refunds)
    ("order_item_refunds.order_item_id", "order_items.order_item_id", True),
    # 13. products[product_id] -> order_items[product_id] (Active, 1:*)
    ("order_items.product_id", "products.product_id", True),
    # 14. Dim_PrimaryProduct[Primary product_id] -> orders[primary_product_id] (Active, 1:*)
    ("orders.primary_product_id", "Dim_PrimaryProduct.'Primary product_id'", True),
]

rel_lines = []
for from_c, to_c, is_act in relationships_list:
    rel_lines.append(f"relationship {uid()}")
    if not is_act:
        rel_lines.append("\tisActive: false")
    rel_lines.append("\tcrossFilteringBehavior: oneDirection")
    rel_lines.append(f"\tfromColumn: {from_c}")
    rel_lines.append(f"\ttoColumn: {to_c}")
    rel_lines.append("")

with open(os.path.join(base_dir, "relationships.tmdl"), "w", encoding="utf-8") as f:
    f.write("\n".join(rel_lines) + "\n")
print("Wrote: relationships.tmdl")


# ==============================================================================
# STEP 1/2: definition/model.tmdl
# ==============================================================================
m_query_order = [
    "website_pageviews",
    "website_sessions",
    "orders",
    "order_items",
    "order_item_refunds",
    "products",
    "Dim_PrimaryProduct",
    "Dim_Customer"
]

all_table_names = list(tables_map.keys())

model_lines = [
    "model Model",
    "\tculture: en-US",
    "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
    "\tsourceQueryCulture: en-US",
    "\tvalueFilterBehavior: independent",
    "\tdataAccessOptions",
    "\t\tlegacyRedirects",
    "\t\treturnErrorValuesAsNull",
    "",
    "annotation __PBI_TimeIntelligenceEnabled = 0",
    "",
    "annotation PBI_QueryOrder = " + str(m_query_order).replace("'", '"'),
    "",
    'annotation PBI_ProTooling = ["DevMode"]',
    ""
]

for tbl in all_table_names:
    model_lines.append(f"ref table {tbl}")

model_lines.append("")
model_lines.append("ref cultureInfo en-US")
model_lines.append("")

with open(os.path.join(base_dir, "model.tmdl"), "w", encoding="utf-8") as f:
    f.write("\n".join(model_lines) + "\n")
print("Wrote: model.tmdl")
print("Model build completed successfully!")
