from typing import BinaryIO
import pandas as pd
import numpy as np
import io

def book_to_csv_stream(books: list[dict]) -> str:
    df = pd.DataFrame(books)
    
    df['images'] = df['images'].apply(lambda x: '|'.join(x) if x else None)
    stream = io.StringIO()
    df.to_csv(stream, index=False, encoding='utf-8-sig', sep=',')
    return stream.getvalue()
        

def clean_csv(file: BinaryIO) -> list[dict]:
    df = pd.read_csv(file, sep=',', encoding='utf-8')
    df['status'] = None

    df = df.dropna(subset=['name', 'regular_price'])

    df['name'] = df['name'].apply(lambda x: x.strip())
    df['regular_price'] = df['regular_price'].astype(int)
    df['sale_price'] = df['sale_price'].fillna('')
    df['sale_price'].apply(lambda x: int(x) if x else None)

    df['edition'] = df['edition'].astype(str)
    df['edition'] = df['edition'].apply(lambda x: x.split('.')[0])

    # Images
    base_url = 'http://mdsalah.customerserver003003.eurhosting.net/WATERMARKED-2/'
    df['images'] = df['images'].fillna('')
    df['images'] = df['images'].apply(lambda x: [(
        base_url + name.strip().replace(' ', '%20')) for name in x.split('|')] if x else [])

    # Language
    df['language'] = df['ln'].apply(
        lambda x: x.replace('Bn', 'bangla').replace('En', 'english'))

    # Notes
    df['notes'] = df['notes'].fillna('')
    df['notes'] = df['notes'].apply(lambda x: x.strip() if x else None)

    df['condition'] = df['condition'].apply(map_condition)
    
    df['cost'] = df['cost'].astype(str)
    df['cost'] = df['cost'].fillna(0)
    df['cost'] = df['cost'].apply(lambda x: x.split('/')[0] if (x and '/' in x) else x)
    df['cost'] = df['cost'].astype(int)
    
    df['cover'] = df['cover'].fillna('')
    df['cover'] = df['cover'].apply(map_cover)
    
    df.rename(columns={
        'name_alt': 'banglish_name',
    }, inplace=True)
    
    df['qty'] = df['qty'].fillna(0)
    df['quantity'] = df['qty'].astype(int)
    df['quantity'] = df['quantity'].apply(lambda x: x if x > 0 else 0)
    
    df.drop(columns=['ln', 'qty', 'id', 'error'], inplace=True)
    
    df = df.replace(['', np.NAN], None)

    return df.to_dict(orient='records')


def map_condition(condition: str) -> str | None:
    if condition:
        if condition.strip().lower() == 'new':
            return 'new'
        elif condition.strip().lower() == 'old':
            return 'old_good_enough'
    return None

def map_cover(cover: str) -> str | None:
    if cover:
        if cover.strip().lower() == 'hardcover':
            return 'hardcover'
        elif cover.strip().lower() == 'paperback':
            return 'paperback'
    
    return None
