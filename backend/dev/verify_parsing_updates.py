import re
from media_scanner import MediaScanner
from unittest.mock import MagicMock

def test_parsing():
    # Mock scanner just to access parse_filename
    scanner = MediaScanner(MagicMock(), "")
    
    test_cases = [
        # User Case 1: Full Season Pack
        {
            "filename": "6teen.S01.TUBI.WEBRip.AAC2.0.x264-RTN[rartv].mkv",
            "expected_title": "6teen",
            "expected_season": 1,
            "expect_season_pack": True
        },
        # User Case 2: Multi-Season Range (Folder-like, keep as is or add if testing file parsing?)
        # Logic handles folders too. Let's assume it's a folder name, so no extension.
        {
            "filename": "30 Rock S01-S07 COMPLETE", 
            "expected_title": "30 Rock",
            "expected_season": 1,
            "expected_season_end": 7,
            "expect_multi_season": True
        },
        # Control: Normal Episode
        {
            "filename": "The.Office.S03E12.Traveling.Salesmen.1080p.WEB.h264-KOGi.mkv",
            "expected_title": "The Office",
            "expected_season": 3,
            "expected_episode": 12,
            "expect_season_pack": False,
            "expected_release_group": "KOGi"
        },
        # New: Streaming Service & Release Group
        {
            "filename": "The.Boys.S01E01.AMZN.WEB-DL.DDP5.1.H.264-NTB.mkv",
            "expected_title": "The Boys",
            "expected_service": "AMZN",
            "expected_release_group": "NTB",
            "expected_audio": ["DD"] # DDP usually maps to DD or captured? 
        },
        # New: Quality & Audio
        {
            "filename": "Movie.2023.PROPER.1080p.BluRay.REMUX.AVC.DTS-HD.MA.5.1-FGT.mkv",
            "expected_title": "Movie",
            "expected_quality": "PROPER",
            "is_remux": True,
            "expected_release_group": "FGT"
        },
        # User Reported Case: "9-1-1 2018 Seasons 1 to 6 Complete 720p WEB x264 [i_c]"
        {
            "filename": "9-1-1 2018 Seasons 1 to 6 Complete 720p WEB x264 [i_c]",
            "expected_title": "9-1-1",
            "expected_season": 1,
            "expected_season_end": 6,
            "expect_multi_season": True
        },
        # User Reported Case: "Apocalypse.The.Second.World.War.2009.E01.1080p..." (Episode Only)
        {
            "filename": "Apocalypse.The.Second.World.War.2009.E01.1080p.BluRay.x264-TENEIGHTY.mkv",
            "expected_title": "Apocalypse The Second World War",
            "expected_season": None, 
            "expected_episode": 1
        },
        # User Reported Case: "The Money Masters (1996) Part 1.avi"
        {
            "filename": "The Money Masters (1996) Part 1.avi",
            "expected_title": "The Money Masters",
            "expected_episode": 1
        },
        # User Reported Case: "S01E01 - 13 January 1989.mkv" (Start SxxExx)
        {
            "filename": "S01E01 - 13 January 1989.mkv",
            "expected_title": "",
            "expected_season": 1,
            "expected_episode": 1
        }
    ]
    
    print("\n--- Running Parsing Verification ---\n")
    
    passed = 0
    for case in test_cases:
        fname = case["filename"]
        result = scanner.parse_filename(fname, force_type="tv")
        
        print(f"Testing: {fname}")
        if not result:
            print("  FAILED: No result returned")
            continue
            
        print(f"  Result: {result}")
        
        # Verify Matches
        fail = False
        if result["title"] != case["expected_title"]:
            print(f"  MISMATCH: Title {result['title']} != {case['expected_title']}")
            fail = True
        
        if result.get("season") != case.get("expected_season"):
            print(f"  MISMATCH: Season {result.get('season')} != {case.get('expected_season')}")
            fail = True
            
        if case.get("expected_episode") and result.get("episode") != case["expected_episode"]:
             print(f"  MISMATCH: Episode {result.get('episode')} != {case['expected_episode']}")
             fail = True
             
        if case.get("expect_season_pack"):
            if not result.get("is_season_pack"):
                print("  MISMATCH: Expected is_season_pack=True")
                fail = True
        elif result.get("is_season_pack"): # Only fail if we DIDN'T expect it but got it? No, control case expects False
             if case.get("expected_episode"): # If it has an episode, it shouldn't be a pack
                 print("  MISMATCH: Got is_season_pack=True for an episode")
                 fail = True

        if case.get("expect_multi_season"):
            if not result.get("is_multi_season"):
                 print("  MISMATCH: Expected is_multi_season=True")
                 fail = True
            if result.get("season_end") != case["expected_season_end"]:
                 print(f"  MISMATCH: Season End {result.get('season_end')} != {case['expected_season_end']}")
                 fail = True
        
        # Metadata Checks
        if case.get("expected_release_group"):
            if result.get("release_group") != case["expected_release_group"]:
                print(f"  MISMATCH: Release Group {result.get('release_group')} != {case['expected_release_group']}")
                fail = True
        
        if case.get("expected_service"):
            services = result.get("streaming_service", [])
            if case["expected_service"] not in services:
                print(f"  MISMATCH: Service {case['expected_service']} not in {services}")
                fail = True

        if case.get("expected_quality"):
            qualities = result.get("quality_modifier", [])
            if case["expected_quality"] not in qualities:
                print(f"  MISMATCH: Quality {case['expected_quality']} not in {qualities}")
                fail = True

        if not fail:
            print("  PASSED")
            passed += 1
        else:
            print(f"  FAILED: Test case '{fname}' failed checks.")
        print("")
        
    print(f"Total: {passed}/{len(test_cases)} passed.")

if __name__ == "__main__":
    test_parsing()
