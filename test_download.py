"""
Simple test script to diagnose the download issue.
Tests different file names and captures server responses.
"""
import asyncio
import websockets
import json
import os

SERVER_ROOT = "wss://orion.ispatial.survey.ntua.gr"
DOWNLOAD_URI = SERVER_ROOT + "/ws/download"

async def test_download(remote_name, category):
    """Test a single download and capture any messages"""
    print(f"\n{'='*60}")
    print(f"Testing: {remote_name} in category: {category}")
    print(f"{'='*60}")
    
    try:
        async with websockets.connect(
            DOWNLOAD_URI,
            ping_interval=None,
            close_timeout=10
        ) as websocket:
            
            print("✓ Connected to server")
            
            request = {
                "type": "start_download",
                "fileName": remote_name,
                "category": category
            }
            print(f"Sending request: {json.dumps(request, indent=2)}")
            
            await websocket.send(json.dumps(request))
            print("✓ Request sent, waiting for response...")
            
            # Try to receive any response (error message, etc.)
            try:
                # Wait a bit to see if server sends an error message
                response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                message = json.loads(response)
                
                print(f"\n✓ Server responded:")
                print(json.dumps(message, indent=2))
                
                if message.get("type") == "error":
                    print(f"\n❌ SERVER ERROR:")
                    print(f"   Message: {message.get('message', 'No message')}")
                    return "error", message
                elif message.get("type") == "download_ready":
                    print("✓ Download ready! File exists and is available.")
                    return "ready", message
                else:
                    print(f"⚠ Unexpected response type: {message.get('type')}")
                    return "unexpected", message
                    
            except asyncio.TimeoutError:
                print("⚠ No response from server (timeout after 3s)")
                print("   Connection might have closed silently")
                return "timeout", None
                
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"\n❌ Connection closed by server")
        print(f"   Close code: {e.code}")
        print(f"   Close reason: {e.reason if e.reason else '(no reason)'}")
        
        # Code 1006 = abnormal closure (no close frame)
        if e.code == 1006:
            print(f"\n   This usually means:")
            print(f"   - File '{remote_name}' doesn't exist in category '{category}'")
            print(f"   - Server encountered an error processing the request")
            print(f"   - Server rejected the request silently")
        
        return "closed", {"code": e.code, "reason": e.reason}
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {type(e).__name__}: {e}")
        return "exception", str(e)


async def main():
    print("="*60)
    print("DOWNLOAD TEST - Testing different file names")
    print("="*60)
    
    # Test cases - try different variations
    test_cases = [
        # Original attempts
        ("tcn-server-env", "docker_files"),
        ("tcn-server-compose", "docker_files"),
        ("tcn-client-env", "docker_files"),
        ("tcn-client-compose", "docker_files"),
        
        # Variations (common naming patterns)
        ("server-env", "docker_files"),
        ("server-compose", "docker_files"),
        ("client-env", "docker_files"),
        ("client-compose", "docker_files"),
        
        # Different categories
        ("tcn-server-env", "config"),
        ("tcn-server-compose", "config"),
        ("tcn-server-env", "files"),
        ("tcn-server-compose", "files"),
    ]
    
    results = {}
    
    for filename, category in test_cases:
        result, data = await test_download(filename, category)
        results[f"{filename}:{category}"] = result
        
        # If we got a successful response, stop testing
        if result == "ready" or result == "error":
            print(f"\n{'='*60}")
            print("FOUND RESULT - Stopping tests")
            print(f"{'='*60}")
            break
            
        # Small delay between tests
        await asyncio.sleep(0.5)
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    for key, result in results.items():
        status = "✓" if result == "ready" else "❌" if result == "closed" else "⚠"
        print(f"{status} {key}: {result}")
    
    # Recommendations
    print(f"\n{'='*60}")
    print("RECOMMENDATIONS")
    print(f"{'='*60}")
    
    if any(r == "ready" for r in results.values()):
        print("✓ Found a working file! Use that file name and category.")
    elif any(r == "error" for r in results.values()):
        print("⚠ Server sent error messages - check the error details above")
        print("   The file might exist but there's a different issue")
    else:
        print("❌ All tests failed with connection closed (code 1006)")
        print("\n   Possible issues:")
        print("   1. File names don't match what's on the server")
        print("   2. Category name is wrong")
        print("   3. Server requires different request format")
        print("   4. Server is having issues")
        print("\n   Next steps:")
        print("   - Check with server administrator for correct file names")
        print("   - Verify the category name is 'docker_files'")
        print("   - Check if there's documentation about the websocket API")


if __name__ == "__main__":
    asyncio.run(main())


