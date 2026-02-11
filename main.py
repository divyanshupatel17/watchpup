"""
VTOP Authentication System - Main Entry Point
"""
import asyncio
import sys
import os
from dotenv import load_dotenv
from authentication import AuthService, AuthError
from data_service import ProfileInfoService, AttendanceDataService, MarksDataService

# Load environment variables
load_dotenv()


async def main():
    """Main authentication flow"""
    
    print("\n" + "="*70)
    print(" "*15 + "VTOP AUTHENTICATION SYSTEM")
    print(" "*10 + "Python Implementation - VITverse App")
    print("="*70 + "\n")
    
    if len(sys.argv) >= 3:
        username = sys.argv[1]
        password = sys.argv[2]
        semester_id = sys.argv[3] if len(sys.argv) >= 4 else None
    else:
        # Load from environment variables
        username = os.getenv('VTOP_USERNAME', '').strip()
        password = os.getenv('VTOP_PASSWORD', '').strip()
        semester_id = os.getenv('VTOP_SEMESTER_ID', '').strip()
        
        if username and password:
            print(f"Loaded credentials from .env file")
            print(f"Username: {username}")
            if semester_id:
                print(f"Semester ID: {semester_id}")
        else:
            print("No credentials found in .env file")
            print("\nEnter your VTOP credentials:\n")
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            if not semester_id:
                semester_id = input("Semester ID (optional): ").strip()
            print()
    
    if not username or not password:
        print("Error: Username and password are required")
        print("\nUsage:")
        print("  python main.py <username> <password>")
        print("  or run: python main.py (for interactive mode)")
        return
    
    auth_service = AuthService()
    
    try:
        print("Initializing captcha recognition model...")
        await auth_service.initialize('authentication/captcha/vellore_weights.json')
        
        print("\nStarting authentication process...\n")
        
        success, error_code, message = await auth_service.login(
            username=username,
            password=password,
            max_attempts=3
        )
        
        print("\n" + "="*70)
        if success:
            print("AUTHENTICATION SUCCESSFUL!")
            print("="*70)
            
            session_info = auth_service.get_session_info()
            if session_info:
                print("\nSession Information:")
                print(f"   Username: {session_info['username']}")
                print(f"   Login Time: {session_info['loginTime']}")
            
            print("\nYou are now logged into VTOP!")
            print("   The session is ready for data synchronization.")
            
            # Automatically extract profile information
            print("\n" + "="*70)
            print("EXTRACTING DATA FROM VTOP")
            print("="*70)
            
            # Step 1: Profile Information
            print("\n[Step 1/3] Extracting profile information...")
            profile_service = ProfileInfoService(auth_service.session)
            if profile_service.run():
                saved_data = profile_service.get_saved_profile()
                if saved_data:
                    profile = saved_data.get('profile', {})
                    print(f"   Status: Done")
                    if profile.get('name'):
                        print(f"   Name: {profile['name']}")
            else:
                print("   Status: Error - Profile extraction failed")
            
            # Step 2: Attendance Data
            if semester_id:
                print(f"\n[Step 2/3] Extracting attendance data...")
                attendance_service = AttendanceDataService(auth_service.session)
                if attendance_service.run(semester_id):
                    saved_data = attendance_service.get_saved_attendance()
                    if saved_data:
                        metadata = saved_data.get('metadata', {})
                        print(f"   Status: Done")
                        print(f"   Total subjects: {metadata.get('totalSubjects', 0)}")
                        print(f"   Overall attendance: {metadata.get('overallPercentage', 0)}%")
                else:
                    print("   Status: Error - Attendance extraction failed")
            else:
                print(f"\n[Step 2/3] Skipped - No semester ID provided")
            
            # Step 3: Marks Data
            if semester_id:
                print(f"\n[Step 3/3] Extracting marks data...")
                marks_service = MarksDataService(auth_service.session)
                if marks_service.run(semester_id):
                    saved_data = marks_service.get_saved_marks()
                    if saved_data:
                        metadata = saved_data.get('metadata', {})
                        print(f"   Status: Done")
                        print(f"   Total courses: {metadata.get('totalCourses', 0)}")
                        print(f"   Total assessments: {metadata.get('totalAssessments', 0)}")
                else:
                    print("   Status: Error - Marks extraction failed")
            else:
                print(f"\n[Step 3/3] Skipped - No semester ID provided")
            
            print("\n" + "="*70)
            print("DATA EXTRACTION COMPLETE")
            print("="*70)
            print(f"\nAll data saved to: data/")
            
        else:
            print("AUTHENTICATION FAILED")
            print("="*70)
            print(f"\nError Code: {error_code}")
            print(f"Error Type: {AuthError.get_error_type(error_code)}")
            print(f"Message: {message}")
            
            if error_code == AuthError.INVALID_CREDENTIALS:
                print("\nSuggestion: Please check your username and password")
            elif error_code == AuthError.INVALID_CAPTCHA:
                print("\nSuggestion: Captcha recognition failed multiple times")
            elif error_code == AuthError.MAX_ATTEMPTS:
                print("\nSuggestion: Maximum captcha attempts reached")
            elif error_code == AuthError.SERVER_CONNECTION:
                print("\nSuggestion: Could not connect to VTOP server")
            elif error_code == AuthError.ACCOUNT_LOCKED:
                print("\nSuggestion: Your account appears to be locked")
            
            if AuthError.is_retryable(error_code):
                print("\nThis error is retryable. You can try again.")
        
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user")
        print("="*70 + "\n")
    except FileNotFoundError:
        print("\nERROR: Model weights file 'authentication/captcha/vellore_weights.json' not found!")
        print("\nInstructions:")
        print("   1. Download the model weights from your VITverse app repository")
        print("   2. Place 'vellore_weights.json' in authentication/captcha/ directory")
        print("   3. The file should be from: assets/ml/vellore_weights.json")
        print("="*70 + "\n")
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        print("="*70 + "\n")
        import traceback
        traceback.print_exc()
    finally:
        if 'auth_service' in locals():
            auth_service.logout()


def run_tests():
    """Run basic tests to verify setup"""
    print("\n" + "="*70)
    print(" "*20 + "RUNNING SETUP TESTS")
    print("="*70 + "\n")
    
    print("Test 1: Checking imports...")
    try:
        import numpy
        import PIL
        import requests
        from bs4 import BeautifulSoup
        print("All required packages imported successfully")
    except ImportError as e:
        print(f"Missing package: {e}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("\nTest 2: Checking constants...")
    try:
        from authentication.constants import VelloreCaptchaConstants, AuthConstants
        print(f"Constants loaded")
        print(f"   - Character set: {VelloreCaptchaConstants.CHARACTER_SET}")
        print(f"   - Confidence threshold: {VelloreCaptchaConstants.CONFIDENCE_THRESHOLD}")
        print(f"   - VTOP URL: {AuthConstants.VTOP_BASE_URL}")
    except Exception as e:
        print(f"Constants error: {e}")
        return False
    
    print("\nTest 3: Checking model weights file...")
    import os
    weights_path = 'authentication/captcha/vellore_weights.json'
    if os.path.exists(weights_path):
        print("Model weights file found")
        
        size_mb = os.path.getsize(weights_path) / (1024 * 1024)
        print(f"   File size: {size_mb:.2f} MB")
        
        if size_mb < 0.1:
            print("Warning: File seems too small, might be corrupted")
        elif size_mb > 100:
            print("Warning: File seems too large, might be wrong file")
    else:
        print("Model weights file 'authentication/captcha/vellore_weights.json' not found")
        print("   Please download from: assets/ml/vellore_weights.json")
        return False
    
    print("\n" + "="*70)
    print("ALL TESTS PASSED - System is ready!")
    print("="*70 + "\n")
    return True


if __name__ == "__main__":
    import sys
    import io
    
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("\nVTOP Authentication System\n")
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
    else:
        asyncio.run(main())
