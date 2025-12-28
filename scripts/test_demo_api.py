#!/usr/bin/env python3
"""Quick test to verify demo DB API is working."""

import sys
import requests
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

def test_demo_api():
    base_url = "http://localhost:8000"
    
    print("Testing Demo API...")
    print(f"Base URL: {base_url}\n")
    
    # Test health endpoint
    try:
        resp = requests.get(f"{base_url}/health", timeout=2)
        print(f"✓ Health check: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"  DB Path: {data.get('db_path', 'N/A')}")
            print(f"  DB Exists: {data.get('db_exists', 'N/A')}")
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False
    
    # Test products endpoint
    try:
        resp = requests.get(f"{base_url}/api/products?page_size=1", timeout=2)
        print(f"\n✓ Products endpoint: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            products = data.get('products', [])
            if products:
                product = products[0]
                product_id = product.get('product_id')
                print(f"  First product ID: {product_id}")
                
                # Test product detail
                resp2 = requests.get(f"{base_url}/api/products/{product_id}", timeout=2)
                if resp2.status_code == 200:
                    detail = resp2.json()
                    listings = detail.get('listings', [])
                    print(f"  Listings count: {len(listings)}")
                    
                    # Test price history for first listing
                    if listings:
                        listing_id = listings[0].get('listing_id')
                        resp3 = requests.get(f"{base_url}/api/listings/{listing_id}/price-history", timeout=2)
                        if resp3.status_code == 200:
                            history = resp3.json()
                            points = history.get('points', [])
                            print(f"  Price history points for listing {listing_id}: {len(points)}")
                            if points:
                                print(f"  ✓ Price history data available!")
                                print(f"    First point: {points[0]}")
                            else:
                                print(f"  ✗ No price history points!")
                        else:
                            print(f"  ✗ Price history endpoint failed: {resp3.status_code}")
                else:
                    print(f"  ✗ Product detail failed: {resp2.status_code}")
    except Exception as e:
        print(f"✗ Products test failed: {e}")
        return False
    
    print("\n✓ All tests passed!")
    return True

if __name__ == "__main__":
    success = test_demo_api()
    sys.exit(0 if success else 1)

