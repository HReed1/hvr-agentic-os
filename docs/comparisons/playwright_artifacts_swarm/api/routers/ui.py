from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>CRUD Interface</title>
</head>
<body>
    <h1>Items</h1>
    <ul id="itemList"></ul>
    <input type="text" id="itemName" placeholder="Item Name">
    <button id="addItemBtn">Add Item</button>

    <script>
        document.getElementById('addItemBtn').addEventListener('click', async () => {
            const name = document.getElementById('itemName').value;
            const res = await fetch('/items/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name })
            });
            const data = await res.json();
            const li = document.createElement('li');
            li.textContent = data.name;
            document.getElementById('itemList').appendChild(li);
        });

        async function loadItems() {
            const res = await fetch('/items/');
            const data = await res.json();
            const ul = document.getElementById('itemList');
            data.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item.name;
                ul.appendChild(li);
            });
        }
        window.onload = loadItems;
    </script>
</body>
</html>
"""

@router.get("/", response_class=HTMLResponse)
async def read_root():
    return HTML_CONTENT
