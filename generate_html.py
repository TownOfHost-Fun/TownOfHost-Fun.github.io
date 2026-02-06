import csv, html
from pathlib import Path
from datetime import datetime, timedelta, timezone

SERVER_ID = "1399723941722853376"

def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

tickets = read_csv("tickets.csv")
mods = read_csv("mod_versions.csv")
#日本時間にしないとわかんないよ！！！
JST = timezone(timedelta(hours=9))
generated_time = datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")

header = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<link rel="icon" href="TOH_F.ico">
<meta charset="UTF-8">
<title>TownOfHost-Fun Web</title>
<style>
body {{ font-family: Arial, sans-serif; padding: 20px; }}
table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
th {{ background-color: #f2f2f2; cursor: pointer; user-select: none; }}
tr:nth-child(even) {{ background-color: #fafafa; }}
input, select, label {{ padding: 5px; margin: 10px 10px 10px 0; vertical-align: middle; }}
.controls {{ margin-bottom: 10px; }}
.sort-indicator {{ font-size: 0.9em; margin-left: 6px; color: #666; }}
#modsTable th {{ cursor: default; }}
.small {{ font-size: 0.9em; color: #555; }}
.tabs {{ margin-bottom: 20px; }}
.tablink {{ background-color: #f2f2f2; border: none; padding: 10px 20px; cursor: pointer; margin-right: 2px; }}
.tablink.active {{ background-color: #ddd; font-weight: bold; }}
.tabcontent {{ display: none; }}
</style>
</head>
<body>
<h1>TownOfHost-Fun Web</h1>
<p class="small">最終更新: {generated_time}</p>

<div style="margin:20px 0;">
<iframe src="https://discord.com/widget?id=1399723941722853376&theme=dark"
        width="350"
        height="500"
        allowtransparency="true"
        frameborder="0"
        sandbox="allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts">
</iframe>
</div>

<div class="tabs">
<button class="tablink active" onclick="openTab(event,'ticketsTab')">チケット</button>
<button class="tablink" onclick="openTab(event,'modsTab')">バージョン</button>
</div>

<div id="ticketsTab" class="tabcontent" style="display:block;">
<h2>チケット</h2>
<div class="controls">
<label for="statusFilter">ステータスで絞り込み：</label>
<select id="statusFilter" onchange="filterTickets()">
<option value="">全て</option>
<option value="open">⚠️未修正</option>
<option value="closed">✅修正済み</option>
</select>
<label for="titleSearch">タイトルで検索：</label>
<input type="text" id="titleSearch" onkeyup="filterTickets()" placeholder="タイトルで検索">
<span class="small">「ID」をクリックして昇順/降順を切り替えることができます</span><br>
<span class="small">データは約1時間ごとに更新されます。</span><br>
<span class="small">「✅修正済み」は、次回のアップデートで修正されるものも含まれます。</span>
</div>

<table id="ticketsTable">
<thead>
<tr>
<th id="idHeader" onclick="toggleSortById()">ID <span id="idSortIndicator" class="sort-indicator">↑</span></th>
<th>バージョン</th>
<th>ステータス</th>
<th>タイトル</th>
<th></th>
</tr>
</thead>
<tbody>
"""

tickets_rows = ""
for row in tickets:
    channel_id = str(row.get("channel_id", ""))
    channel_link = f"https://discord.com/channels/{SERVER_ID}/{channel_id}"

    status_raw = row.get("status", "").lower()
    status_jp = "⚠️未修正" if status_raw == "open" else "✅修正済み"

    tickets_rows += (
        f"<tr data-status='{html.escape(status_raw)}'>"
        f"<td>{html.escape(str(row.get('id', '')))}</td>"
        f"<td>{html.escape(str(row.get('version', '')))}</td>"
        f"<td>{html.escape(status_jp)}</td>"
        f"<td>{html.escape(str(row.get('title', '')))}</td>"
        f"<td><a target='_blank' href='{html.escape(channel_link)}'>🔗</a></td>"
        f"</tr>"
    )


tickets_end = """
</tbody>
</table>
</div>

<div id="modsTab" class="tabcontent">
<div class="controls">
<label for="versionSearch">バージョン検索：</label>
<input type="text" id="versionSearch" placeholder="部分文字列で絞り込み" oninput="buildModsTable()">
<label for="includeBeta"><input type="checkbox" id="includeBeta" checked onchange="buildModsTable()"> β を含める</label>
</div>
<ul id="modsList" style="display:none">
"""

mods_li = "".join(f"<li>{html.escape(row.get('version',''))}</li>" for row in mods)

#うわ、長い...
mods_end = """
</ul>
<div id="modsContainer"></div>
<script>
var idSortAscending = true;

function parseIdForSort(text){
    var n = parseInt(text, 10);
    return isNaN(n) ? text.toLowerCase() : n;
}

function toggleSortById(){
    var tbody = document.querySelector("#ticketsTable tbody");
    var rows = Array.from(tbody.querySelectorAll("tr"));

    rows.sort(function(a,b){
        var aId = parseIdForSort(a.cells[0].textContent.trim());
        var bId = parseIdForSort(b.cells[0].textContent.trim());
        if(aId < bId) return idSortAscending ? -1 : 1;
        if(aId > bId) return idSortAscending ? 1 : -1;
        return 0;
    });

    rows.forEach(function(r){ tbody.appendChild(r); });

    document.getElementById("idSortIndicator").textContent = idSortAscending ? "↓" : "↑";
    idSortAscending = !idSortAscending;
}

function filterTickets(){
    var status = document.getElementById("statusFilter").value.toLowerCase();
    var search = document.getElementById("titleSearch").value.toLowerCase();
    var trs = document.querySelectorAll("#ticketsTable tbody tr");

    trs.forEach(function(tr){
        var tds = tr.getElementsByTagName("td");
        if(tds.length < 5){
            tr.style.display = "";
            return;
        }
        
        var rowStatus = tr.dataset.status;

        var rowTitle = tds[3].textContent.toLowerCase();

        var visible =
            (status === "" || rowStatus === status) &&
            rowTitle.includes(search);

        tr.style.display = visible ? "" : "none";
    });
}


document.addEventListener("DOMContentLoaded", function(){
    try{
        toggleSortById();  // 初期ソート維持
        toggleSortById();  // 昇順に戻す
    }catch(e){}
    buildModsTable();
});

function extractDigitsArray(ver){
    var parts = ver.match(/\d+/g) || [];
    return parts.map(function(p){ return parseInt(p, 10); });
}

function versionHasBeta(ver){
    return /β|beta/i.test(ver);
}

function compareVersionStrings(a,b){
    var ap = extractDigitsArray(a);
    var bp = extractDigitsArray(b);
    var len = Math.max(ap.length, bp.length);

    for(var i=0;i<len;i++){
        var ai = (i < ap.length) ? ap[i] : 0;
        var bi = (i < bp.length) ? bp[i] : 0;
        if(ai < bi) return -1;
        if(ai > bi) return 1;
    }

    var aBeta = versionHasBeta(a);
    var bBeta = versionHasBeta(b);

    if(aBeta && !bBeta) return 1;
    if(!aBeta && bBeta) return -1;

    return a.localeCompare(b);
}

function buildModsTable(){
    var includeBeta = document.getElementById("includeBeta").checked;
    var filter = document.getElementById("versionSearch").value.toLowerCase();

    var rawLis = Array.from(document.querySelectorAll("#modsList li"));
    var versions = rawLis.map(li => li.textContent.trim()).filter(Boolean);

    versions = versions.filter(function(v){
        if(!includeBeta && versionHasBeta(v)) return false;
        if(filter && !v.toLowerCase().includes(filter)) return false;
        return true;
    });

    var groups = {};
    versions.forEach(function(v){
        var parts = extractDigitsArray(v);
        var major = (parts.length > 0 ? String(parts[0]) : "0");
        if(!groups[major]) groups[major] = [];
        groups[major].push(v);
    });

    var majors = Object.keys(groups)
        .map(n => parseInt(n, 10))
        .sort((a,b)=>a-b)
        .map(String);

    majors.forEach(function(m){
        groups[m].sort(compareVersionStrings);
    });

    var maxRows = Math.max(...majors.map(m => groups[m].length));

    var container = document.getElementById("modsContainer");
    container.innerHTML = "";

    if(majors.length === 0){
        container.innerHTML = "<p class='small'>バージョンが見つかりません。</p>";
        return;
    }

    var table = document.createElement("table");
    table.id = "modsTable";

    var thead = document.createElement("thead");
    var headerRow = document.createElement("tr");
    majors.forEach(function(m){
        var th = document.createElement("th");
        th.textContent = "Major " + m;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    var tbody = document.createElement("tbody");
    for(var r=0;r<maxRows;r++){
        var tr = document.createElement("tr");
        majors.forEach(function(m){
            var td = document.createElement("td");
            td.textContent = groups[m][r] || "";
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    }
    table.appendChild(tbody);
    container.appendChild(table);
}

function openTab(evt, tabName){
    var tabcontents = document.getElementsByClassName("tabcontent");
    for(var i=0;i<tabcontents.length;i++){
        tabcontents[i].style.display = "none";
    }
    var tablinks = document.getElementsByClassName("tablink");
    for(var i=0;i<tablinks.length;i++){
        tablinks[i].classList.remove("active");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.classList.add("active");
}
</script>

</body>
</html>
"""

full_html = header + tickets_rows + tickets_end + mods_li + mods_end

out_dir = Path("public")
out_dir.mkdir(exist_ok=True)
(out_dir / "index.html").write_text(full_html, encoding="utf-8")
print("Generated public/index.html")
