import os
import uuid

def uid():
    return str(uuid.uuid4())

base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Maven Fuzzy Factory.SemanticModel", "definition")
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
        if " " in sc or "%" in sc or "$" in sc or "-" in sc:
            lines.append(f"\t\tsourceColumn: {sc}")
        else:
            lines.append(f"\t\tsourceColumn: {sc}")
    lines.append("")
    return "\n".join(lines)

# ==============================================================================
# 1. products
# ==============================================================================
products_cols = [
    col("product_id", "int64", is_source=True, format_str="0"),
    col("created_at", "dateTime", is_source=True, format_str="General Date"),
    col("product_name", "string", is_source=True),
    col("Retail Price", "double", is_source=True, source_col="Retail Price", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("Unit COGS", "double", is_source=True, source_col="Unit COGS", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("Margin $", "double", is_source=True, source_col="Margin $", format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("Margin %", "double", is_source=True, source_col="Margin %", format_str="0.00%"),
    col("Product Role", "string", is_source=True, source_col="Product Role")
]

products_m = '''\tpartition products = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t  Source = Csv.Document(File.Contents("F:\\MAVEN DATA\\Maven+Fuzzy+Factory\\products.csv"), [Delimiter = ",", Columns = 3, QuoteStyle = QuoteStyle.None]),
\t\t\t\t  #"Promoted headers" = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
\t\t\t\t  #"Changed column type" = Table.TransformColumnTypes(#"Promoted headers", {{"product_id", Int64.Type}, {"created_at", type datetime}, {"product_name", type text}}),
\t\t\t\t  #"Added Retail Price" = Table.AddColumn(#"Changed column type", "Retail Price", each if [product_id] = 1 then 49.99 else if [product_id] = 2 then 59.99 else if [product_id] = 3 then 45.99 else 29.99, type number),
\t\t\t\t  #"Added Unit COGS" = Table.AddColumn(#"Added Retail Price", "Unit COGS", each if [product_id] = 1 then 19.49 else if [product_id] = 2 then 22.49 else if [product_id] = 3 then 14.49 else 9.49, type number),
\t\t\t\t  #"Added Margin $" = Table.AddColumn(#"Added Unit COGS", "Margin $", each [Retail Price] - [Unit COGS], type number),
\t\t\t\t  #"Added Margin %" = Table.AddColumn(#"Added Margin $", "Margin %", each [#"Margin $"] / [Retail Price], type number),
\t\t\t\t  #"Added Product Role" = Table.AddColumn(#"Added Margin %", "Product Role", each if [product_id] = 1 then "Flagship Launch Bear" else if [product_id] = 2 then "Premium Valentine's" else if [product_id] = 3 then "Birthday Gift" else "Cross-Sell Add-on", type text)
\t\t\t\tin
\t\t\t\t  #"Added Product Role"

\tannotation PBI_ResultType = Table
'''
products_tmdl = f"table products\n\tlineageTag: {uid()}\n\n" + "\n".join(products_cols) + "\n" + products_m

# ==============================================================================
# 2. orders
# ==============================================================================
orders_cols = [
    col("order_id", "int64", is_source=True, format_str="0"),
    col("created_at", "dateTime", is_source=True, format_str="General Date"),
    col("website_session_id", "int64", is_source=True, format_str="0"),
    col("user_id", "int64", is_source=True, format_str="0"),
    col("primary_product_id", "int64", is_source=True, format_str="0"),
    col("items_purchased", "int64", is_source=True, format_str="0"),
    col("price_usd", "double", is_source=True, format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("cogs_usd", "double", is_source=True, format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("Order Date", "dateTime", is_source=True, source_col="Order Date", format_str="yyyy-MM-dd"),
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
\t\t\t\t  #"Added Basket Type" = Table.AddColumn(#"Added Order Date", "Basket Type", each if [items_purchased] = 1 then "Single" else "Bundle", type text),
\t\t\t\t  #"Added Margin $" = Table.AddColumn(#"Added Basket Type", "Margin $", each [price_usd] - [cogs_usd], type number),
\t\t\t\t  #"Added Margin %" = Table.AddColumn(#"Added Margin $", "Margin %", each if [price_usd] = 0 or [price_usd] = null then 0 else ([price_usd] - [cogs_usd]) / [price_usd], type number)
\t\t\t\tin
\t\t\t\t  #"Added Margin %"

\tannotation PBI_ResultType = Table
'''
orders_tmdl = f"table orders\n\tlineageTag: {uid()}\n\n" + "\n".join(orders_cols) + "\n" + orders_m

# ==============================================================================
# 3. order_items
# ==============================================================================
order_items_cols = [
    col("order_item_id", "int64", is_source=True, format_str="0"),
    col("created_at", "dateTime", is_source=True, format_str="General Date"),
    col("order_id", "int64", is_source=True, format_str="0"),
    col("product_id", "int64", is_source=True, format_str="0"),
    col("is_primary_item", "int64", is_source=True, format_str="0"),
    col("price_usd", "double", is_source=True, format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("cogs_usd", "double", is_source=True, format_str=r"\$#,0.00;(\$#,0.00);\$#,0.00"),
    col("Order Date", "dateTime", is_source=True, source_col="Order Date", format_str="yyyy-MM-dd"),
    col("Item Role", "string", is_source=True, source_col="Item Role"),
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
\t\t\t\t  #"Added Item Role" = Table.AddColumn(#"Added Order Date", "Item Role", each if [is_primary_item] = 1 then "Primary Item" else "Cross-Sell Item", type text),
\t\t\t\t  #"Added Margin $" = Table.AddColumn(#"Added Item Role", "Margin $", each [price_usd] - [cogs_usd], type number),
\t\t\t\t  #"Added Margin %" = Table.AddColumn(#"Added Margin $", "Margin %", each if [price_usd] = 0 or [price_usd] = null then 0 else ([price_usd] - [cogs_usd]) / [price_usd], type number)
\t\t\t\tin
\t\t\t\t  #"Added Margin %"

\tannotation PBI_ResultType = Table
'''
order_items_tmdl = f"table order_items\n\tlineageTag: {uid()}\n\n" + "\n".join(order_items_cols) + "\n" + order_items_m

# ==============================================================================
# 4. order_item_refunds
# ==============================================================================
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
    col("Refund Date", "dateTime", is_source=True, source_col="Refund Date", format_str="yyyy-MM-dd"),
    col("Lag Days", "int64", dax_calc="DATEDIFF(LOOKUPVALUE(orders[created_at], orders[order_id], [order_id]), [created_at], DAY)", format_str="0"),
    col("Lag Bucket", "string", dax_calc='SWITCH(TRUE(), [Lag Days] <= 5, "2-5 Days", [Lag Days] <= 10, "6-10 Days", "11-16 Days")')
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
# 5. website_sessions
# ==============================================================================
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
    col("Session Date", "dateTime", is_source=True, source_col="Session Date", format_str="yyyy-MM-dd"),
    col("Channel Grouping", "string", is_source=True, source_col="Channel Grouping"),
    col("Traffic Type", "string", is_source=True, source_col="Traffic Type"),
    col("Chapter ID", "int64", is_source=True, source_col="Chapter ID", format_str="0"),
    col("Pageviews", "int64", dax_calc="COUNTROWS(RELATEDTABLE(website_pageviews))", format_str="0"),
    col("Is Bounce", "int64", dax_calc="IF([Pageviews] = 1, 1, 0)", format_str="0")
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
\t\t\t\t  #"Added Channel Grouping" = Table.AddColumn(#"Added Session Date", "Channel Grouping", each if [utm_source] = null and [http_referer] = null then "Direct Type-In" else if [utm_source] = null and [http_referer] <> null then "Organic Search" else if [utm_source] = "gsearch" and [utm_campaign] = "brand" then "Paid: Google Brand" else if [utm_source] = "gsearch" and [utm_campaign] = "nonbrand" then "Paid: Google Nonbrand" else if [utm_source] = "bsearch" and [utm_campaign] = "brand" then "Paid: Bing Brand" else if [utm_source] = "bsearch" and [utm_campaign] = "nonbrand" then "Paid: Bing Nonbrand" else if [utm_source] = "socialbook" then "Paid Social" else "Other", type text),
\t\t\t\t  #"Added Traffic Type" = Table.AddColumn(#"Added Channel Grouping", "Traffic Type", each if [utm_source] = null then (if [http_referer] = null then "Direct" else "Organic") else "Paid", type text),
\t\t\t\t  #"Added Chapter ID" = Table.AddColumn(#"Added Traffic Type", "Chapter ID", each if [created_at] >= #datetime(2015, 1, 1, 0, 0, 0) then 5 else if [created_at] >= #datetime(2014, 2, 1, 0, 0, 0) then 4 else if [created_at] >= #datetime(2013, 1, 1, 0, 0, 0) then 3 else if [created_at] >= #datetime(2012, 9, 1, 0, 0, 0) then 2 else 1, Int64.Type)
\t\t\t\tin
\t\t\t\t  #"Added Chapter ID"

\tannotation PBI_ResultType = Table
'''
website_sessions_tmdl = f"table website_sessions\n\tlineageTag: {uid()}\n\n" + "\n".join(sessions_cols) + "\n" + sessions_m

# ==============================================================================
# 6. website_pageviews
# ==============================================================================
pv_cols = [
    col("website_pageview_id", "int64", is_source=True, format_str="0"),
    col("created_at", "dateTime", is_source=True, format_str="General Date"),
    col("website_session_id", "int64", is_source=True, format_str="0"),
    col("pageview_url", "string", is_source=True),
    col("Pageview Date", "dateTime", is_source=True, source_col="Pageview Date", format_str="yyyy-MM-dd"),
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
\t\t\t\t  #"Added Page Category" = Table.AddColumn(#"Added Pageview Date", "Page Category", each if List.Contains({"/home", "/lander-1", "/lander-2", "/lander-3", "/lander-4", "/lander-5"}, [pageview_url]) then "Landing Page" else if [pageview_url] = "/products" then "Catalog" else if List.Contains({"/the-original-mr-fuzzy", "/the-forever-love-bear", "/the-birthday-sugar-panda", "/the-hudson-river-mini-bear"}, [pageview_url]) then "Product Detail" else if List.Contains({"/cart", "/shipping", "/billing", "/billing-2"}, [pageview_url]) then "Checkout Funnel" else if [pageview_url] = "/thank-you-for-your-order" then "Conversion" else "Other", type text)
\t\t\t\tin
\t\t\t\t  #"Added Page Category"

\tannotation PBI_ResultType = Table
'''
website_pageviews_tmdl = f"table website_pageviews\n\tlineageTag: {uid()}\n\n" + "\n".join(pv_cols) + "\n" + pv_m

# ==============================================================================
# Write base CSV tables
# ==============================================================================
with open(os.path.join(tables_dir, "products.tmdl"), "w", encoding="utf-8") as f:
    f.write(products_tmdl)

with open(os.path.join(tables_dir, "orders.tmdl"), "w", encoding="utf-8") as f:
    f.write(orders_tmdl)

with open(os.path.join(tables_dir, "order_items.tmdl"), "w", encoding="utf-8") as f:
    f.write(order_items_tmdl)

with open(os.path.join(tables_dir, "order_item_refunds.tmdl"), "w", encoding="utf-8") as f:
    f.write(order_item_refunds_tmdl)

with open(os.path.join(tables_dir, "website_sessions.tmdl"), "w", encoding="utf-8") as f:
    f.write(website_sessions_tmdl)

with open(os.path.join(tables_dir, "website_pageviews.tmdl"), "w", encoding="utf-8") as f:
    f.write(website_pageviews_tmdl)

# ==============================================================================
# Clean relationships.tmdl
# ==============================================================================
relationships_content = f"""relationship 780db2d4-117d-491d-a3de-5f36d98d6a5d
\tjoinOnDateBehavior: datePartOnly
\tfromColumn: order_item_refunds.created_at
\ttoColumn: LocalDateTable_1580720a-eb97-4948-bb47-5b731dcf40a7.Date

relationship {uid()}
\tfromColumn: orders.'Order Date'
\ttoColumn: Dim_Date.Date

relationship {uid()}
\tisActive: false
\tfromColumn: order_items.'Order Date'
\ttoColumn: Dim_Date.Date

relationship {uid()}
\tfromColumn: website_sessions.'Session Date'
\ttoColumn: Dim_Date.Date

relationship {uid()}
\tfromColumn: order_item_refunds.'Refund Date'
\ttoColumn: Dim_Date.Date

relationship {uid()}
\tfromColumn: order_items.product_id
\ttoColumn: products.product_id

relationship {uid()}
\tfromColumn: order_items.order_id
\ttoColumn: orders.order_id

relationship {uid()}
\tfromColumn: website_pageviews.website_session_id
\ttoColumn: website_sessions.website_session_id

"""

with open(os.path.join(base_dir, "relationships.tmdl"), "w", encoding="utf-8") as f:
    f.write(relationships_content)

# All tables generated cleanly
