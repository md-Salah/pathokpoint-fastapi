import io
import pytest
from httpx import AsyncClient
from starlette import status
import pandas as pd
from unittest.mock import MagicMock

pytestmark = pytest.mark.asyncio


async def test_export_books(client: AsyncClient, book_in_db: dict, admin_auth_headers: dict):
    response = await client.get("/book/export/csv", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.headers.get("Content-Disposition") is not None
    assert response.headers.get("Content-Type") == "text/csv; charset=utf-8"
    assert response.content.startswith(
        b"id,sku,name,regular_price,sale_price,quantity,manage_stock,authors,publisher,categories,images,tags,")
    assert len(response.content.splitlines()) == 2


async def test_import_books_by_csv(mock_upload_file: MagicMock, mock_delete_file: MagicMock, send_email: MagicMock, client: AsyncClient, admin_in_db_with_token: dict):
    mock_upload_file.return_value = 'key'
    mock_delete_file.return_value = True
    send_email.return_value = None
    headers = {
        'Authorization': "Bearer {}".format(admin_in_db_with_token['token'])
    }

    data = [
        {'condition': 'old-good-enough',
         'authors': 'S.K. Tremayne',
         'authors_slug': 's-k-tremayne',
         'images': 'https://res.cloudinary.com/test_book.jpg',
         'cover': 'paperback',
         'name': 'The Fire Child',
         'slug': 'the-fire-child-original',
         'stock_location': 'mirpur-11',
         'quantity': 1,
         'sku': '200-3257',
         'publisher': 'Harper',
         'sale_price': 250.0,
         'tags': 'English-OLD',
         'is_used': True,
         'manage_stock': True,
         'language': 'english',
         'in_stock': True,
         'regular_price': 250.0},
        {'condition': 'old-like-new',
         'authors': 'আতিউর রহমান | Motin',
         'cover': 'hardcover',
         'name': 'শেখ মুজিব বাংলাদেশের আরেক নাম',
         'slug': 'shekh-mujib-bangladesher-arek-nam',
         'stock_location': 'mirpur-11',
         'quantity': 1,
         'sku': '201-2919',
         'publisher': 'আলোঘর প্রকাশনা',
         'sale_price': 550.0,
         'tags': 'Bangla-OLD',
         'is_used': True,
         'manage_stock': True,
         'language': 'bangla',
         'in_stock': True,
         'regular_price': 550.0},
        {'condition': 'old-good-enough',
         'categories': 'Fiction',
         'cover': '',
         'name': 'ব্রেইন বুস্টার',
         'slug': 'brein-busttaar',
         'stock_location': 'mirpur-11',
         'quantity': 1,
         'sku': '29-158',
         'publisher': 'অধ্যয়ন',
         'sale_price': 165.0,
         'tags': 'Bangla-OLD',
         'is_used': True,
         'manage_stock': True,
         'language': '',
         'in_stock': True,
         'regular_price': 165.0},
        {'condition': 'old-good-enough',
         'cover': 'paperback',
         'name': 'Socialite Evenings',
         'slug': 'socialite-evenings-original',
         'stock_location': 'mirpur-11',
         'quantity': 2,
         'sku': '201-4309',
         'publisher': 'penguin',
         'sale_price': 260.0,
         'tags': 'English-OLD',
         'is_used': True,
         'manage_stock': True,
         'language': 'english',
         'in_stock': True,
         'regular_price': 260.0}]

    df = pd.DataFrame(data)

    csv_content = df.to_csv(index=False).encode("utf-8")
    file = io.BytesIO(csv_content)
    files = [
        ('file', ('test_books.csv', file, 'text/csv'))
    ]
    response = await client.post("/book/import/csv", files=files, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    mock_upload_file.assert_called_once
    mock_delete_file.assert_not_called
    send_email.assert_called_once

    # Test update books
    payload = []
    for book in data:
        payload.append({
            'sku': book['sku'],
            'quantity': 100,
            'images': book.get('images', []),
        })
    df = pd.DataFrame(payload)
    csv_content = df.to_csv(index=False).encode("utf-8")
    file = io.BytesIO(csv_content)
    files = [
        ('file', ('test_books.csv', file, 'text/csv'))
    ]
    response = await client.post("/book/import/csv", files=files, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    mock_upload_file.assert_called_once
    mock_delete_file.assert_called_once
    send_email.assert_called_once
