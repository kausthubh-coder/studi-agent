import aiohttp
import json
import logging
import datetime
from typing import Dict, List, Any, Optional

# Import with compatibility for both running directly and as part of package
try:
    # When running from within the agent directory
    from config import CANVAS_API_URL, CANVAS_ACCESS_TOKEN, CANVAS_INSTITUTE_URL
except ImportError:
    # When running as part of the agent package
    from agent.config import CANVAS_API_URL, CANVAS_ACCESS_TOKEN, CANVAS_INSTITUTE_URL

# Set up logging
logger = logging.getLogger("canvas_client")
logger.setLevel(logging.DEBUG)

class CanvasClient:
    """Client for interacting with Canvas API"""
    
    def __init__(self, debug=False, institute_url=None):
        """Initialize the Canvas client with API URL and token from config"""
        self.api_url = CANVAS_API_URL
        self.token = CANVAS_ACCESS_TOKEN
        self.institute_url = institute_url or CANVAS_INSTITUTE_URL
        self.headers = {
            "Content-Type": "application/json"
        }
        self.debug = debug
        logger.info(f"Canvas client initialized with API URL: {self.api_url}")
        logger.info(f"Using institute URL: {self.institute_url}")
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        Make a request to the Canvas API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., '/courses')
            data: Optional data for POST/PUT requests
            
        Returns:
            Response data as a dictionary
        """
        url = f"{self.api_url}{endpoint}"
        
        # Create query parameters with institute_url and token
        params = {
            "institute_url": self.institute_url,
            "token": self.token
        }
        
        # Log the request details
        logger.debug(f"Making {method} request to {url}")
        if self.debug:
            print(f"DEBUG: Making {method} request to {url}")
            print(f"DEBUG: Query parameters: institute_url={self.institute_url}, token={self.token[:5]}...")
            print(f"DEBUG: Headers: {json.dumps(self.headers, indent=2)}")
            if data:
                print(f"DEBUG: Data: {json.dumps(data, indent=2)}")
        
        async with aiohttp.ClientSession() as session:
            try:
                if method == "GET":
                    async with session.get(url, params=params, headers=self.headers) as response:
                        response_text = await response.text()
                        if self.debug:
                            print(f"DEBUG: Response status: {response.status}")
                            print(f"DEBUG: Response text: {response_text[:500]}...")
                        
                        if response.status == 200:
                            response_json = json.loads(response_text)
                            if response_json.get("success", False):
                                return response_json.get("data", {})
                            else:
                                error_message = response_json.get("error", "Unknown error")
                                logger.error(f"Canvas API error: {error_message}")
                                raise Exception(f"Canvas API error: {error_message}")
                        else:
                            logger.error(f"Canvas API error ({response.status}): {response_text}")
                            raise Exception(f"Canvas API error ({response.status}): {response_text}")
                
                elif method == "POST":
                    async with session.post(url, params=params, headers=self.headers, json=data) as response:
                        response_text = await response.text()
                        if self.debug:
                            print(f"DEBUG: Response status: {response.status}")
                            print(f"DEBUG: Response text: {response_text}")
                            
                        if response.status == 200:
                            response_json = json.loads(response_text)
                            if response_json.get("success", False):
                                return response_json.get("data", {})
                            else:
                                error_message = response_json.get("error", "Unknown error")
                                logger.error(f"Canvas API error: {error_message}")
                                raise Exception(f"Canvas API error: {error_message}")
                        else:
                            logger.error(f"Canvas API error ({response.status}): {response_text}")
                            raise Exception(f"Canvas API error ({response.status}): {response_text}")
                
                elif method == "PUT":
                    async with session.put(url, params=params, headers=self.headers, json=data) as response:
                        response_text = await response.text()
                        if self.debug:
                            print(f"DEBUG: Response status: {response.status}")
                            print(f"DEBUG: Response text: {response_text}")
                            
                        if response.status == 200:
                            response_json = json.loads(response_text)
                            if response_json.get("success", False):
                                return response_json.get("data", {})
                            else:
                                error_message = response_json.get("error", "Unknown error")
                                logger.error(f"Canvas API error: {error_message}")
                                raise Exception(f"Canvas API error: {error_message}")
                        else:
                            logger.error(f"Canvas API error ({response.status}): {response_text}")
                            raise Exception(f"Canvas API error ({response.status}): {response_text}")
                
                elif method == "DELETE":
                    async with session.delete(url, params=params, headers=self.headers) as response:
                        response_text = await response.text()
                        if self.debug:
                            print(f"DEBUG: Response status: {response.status}")
                            print(f"DEBUG: Response text: {response_text}")
                            
                        if response.status == 200:
                            try:
                                response_json = json.loads(response_text)
                                if response_json.get("success", False):
                                    return response_json.get("data", {})
                                else:
                                    error_message = response_json.get("error", "Unknown error")
                                    logger.error(f"Canvas API error: {error_message}")
                                    raise Exception(f"Canvas API error: {error_message}")
                            except json.JSONDecodeError:
                                return {"status": "success"}
                        else:
                            logger.error(f"Canvas API error ({response.status}): {response_text}")
                            raise Exception(f"Canvas API error ({response.status}): {response_text}")
            except aiohttp.ClientError as e:
                logger.error(f"Network error when connecting to Canvas API: {str(e)}")
                raise Exception(f"Network error when connecting to Canvas API: {str(e)}")
    
    # Courses
    async def get_courses(self) -> List[Dict]:
        """Get list of courses"""
        logger.info("Retrieving list of courses")
        return await self._make_request("GET", "/courses")
    
    async def get_course(self, course_id: int) -> Dict:
        """Get course details"""
        return await self._make_request("GET", f"/courses/{course_id}")
    
    # Assignments
    async def get_assignments(self, course_id: int) -> List[Dict]:
        """Get list of assignments for a course"""
        return await self._make_request("GET", f"/courses/{course_id}/assignments")
    
    async def get_assignment(self, course_id: int, assignment_id: int) -> Dict:
        """Get assignment details"""
        return await self._make_request("GET", f"/courses/{course_id}/assignments/{assignment_id}")
    
    async def get_assignment_details(self, course_id: int, assignment_id: int) -> Dict:
        """
        Get comprehensive details about an assignment, including instructions,
        attached files, and submission requirements
        
        Args:
            course_id: The ID of the course
            assignment_id: The ID of the assignment
            
        Returns:
            Dictionary containing detailed assignment information
        """
        # Get the basic assignment data
        assignment_data = await self.get_assignment(course_id, assignment_id)
        
        if not assignment_data:
            return {"error": "Assignment not found"}
            
        # Extract helpful information from the assignment
        details = {
            "id": assignment_data.get("id"),
            "name": assignment_data.get("name"),
            "due_at": assignment_data.get("due_at"),
            "points_possible": assignment_data.get("points_possible"),
            "submission_types": assignment_data.get("submission_types", []),
            "has_submitted_submissions": assignment_data.get("has_submitted_submissions", False),
            "allowed_attempts": assignment_data.get("allowed_attempts", -1),
            "unlock_at": assignment_data.get("unlock_at"),
            "lock_at": assignment_data.get("lock_at"),
            "description": assignment_data.get("description", "No description available"),
        }
        
        # Extract file information from the HTML description if available
        files = []
        description = assignment_data.get("description", "")
        if description and "<a" in description:
            import re
            # Look for file links in the description
            file_matches = re.findall(r'<a[^>]*?title="([^"]*)"[^>]*?href="([^"]*)"', description)
            for title, url in file_matches:
                files.append({
                    "title": title,
                    "url": url
                })
        
        details["files"] = files
        
        # Get additional submission requirements if applicable
        details["requires_submission"] = bool(assignment_data.get("submission_types", []))
        if "online_quiz" in assignment_data.get("submission_types", []):
            details["is_quiz"] = True
        
        # Format due date for more readability if available
        if details.get("due_at"):
            try:
                due_date = datetime.datetime.fromisoformat(details["due_at"].replace('Z', '+00:00'))
                details["formatted_due_date"] = due_date.strftime("%B %d, %Y at %I:%M %p")
            except (ValueError, AttributeError):
                pass
        
        return details
    
    async def find_assignment_by_name(self, course_id: int, name_pattern: str) -> Optional[Dict]:
        """
        Find an assignment by name or partial name
        
        Args:
            course_id: The ID of the course
            name_pattern: Full or partial name of the assignment to find
            
        Returns:
            Assignment data or None if not found
        """
        assignments = await self.get_assignments(course_id)
        
        # Convert name pattern to lowercase for case-insensitive matching
        name_pattern = name_pattern.lower()
        
        for assignment in assignments:
            assignment_name = assignment.get("name", "").lower()
            # Check if pattern is in the name
            if name_pattern in assignment_name:
                return assignment
                
        return None
    
    # Submissions
    async def get_submissions(self, course_id: int, assignment_id: int) -> List[Dict]:
        """Get submissions for an assignment"""
        return await self._make_request("GET", f"/courses/{course_id}/assignments/{assignment_id}/submissions")
    
    # Announcements
    async def get_announcements(self, course_id: int) -> List[Dict]:
        """Get announcements for a course"""
        return await self._make_request("GET", f"/courses/{course_id}/announcements")
    
    # Files
    async def get_files(self, course_id: int) -> List[Dict]:
        """Get files for a course"""
        return await self._make_request("GET", f"/courses/{course_id}/files")
    
    # Modules
    async def get_modules(self, course_id: int) -> List[Dict]:
        """Get modules for a course"""
        return await self._make_request("GET", f"/courses/{course_id}/modules")
    
    async def get_module_items(self, course_id: int, module_id: int) -> List[Dict]:
        """Get items in a module"""
        return await self._make_request("GET", f"/courses/{course_id}/modules/{module_id}/items")
    
    # User
    async def get_user_profile(self) -> Dict:
        """Get current user profile"""
        return await self._make_request("GET", "/users/self")
    
    # Grades
    async def get_grades(self, course_id: int) -> Dict:
        """Get grades for a course"""
        return await self._make_request("GET", f"/courses/{course_id}/grades")
    
    # Assignments with new methods focused on relevant information
    async def get_upcoming_assignments(self, course_id: int, days: int = 14) -> List[Dict]:
        """
        Get assignments due in the next X days for a course
        
        Args:
            course_id: The ID of the course
            days: Number of days to look ahead (default 14)
            
        Returns:
            List of upcoming assignments
        """
        all_assignments = await self.get_assignments(course_id)
        
        # Get current date
        now = datetime.datetime.now()
        cutoff_date = now + datetime.timedelta(days=days)
        
        # Filter for upcoming assignments
        upcoming = []
        for assignment in all_assignments:
            # Skip if no due date or already submitted
            if not assignment.get("due_at") or assignment.get("submitted", False):
                continue
                
            # Parse due date
            try:
                due_date = datetime.datetime.fromisoformat(assignment.get("due_at").replace('Z', '+00:00'))
                if now < due_date <= cutoff_date:
                    upcoming.append(assignment)
            except (ValueError, AttributeError):
                # Skip assignments with invalid date format
                continue
                
        return upcoming
    
    async def get_late_assignments(self, course_id: int) -> List[Dict]:
        """
        Get assignments that are past due and not submitted
        
        Args:
            course_id: The ID of the course
            
        Returns:
            List of late assignments
        """
        all_assignments = await self.get_assignments(course_id)
        
        # Get current date
        now = datetime.datetime.now()
        
        # Filter for late assignments
        late = []
        for assignment in all_assignments:
            # Skip if no due date or already submitted
            if not assignment.get("due_at") or assignment.get("submitted", False):
                continue
                
            # Parse due date
            try:
                due_date = datetime.datetime.fromisoformat(assignment.get("due_at").replace('Z', '+00:00'))
                if due_date < now:
                    late.append(assignment)
            except (ValueError, AttributeError):
                # Skip assignments with invalid date format
                continue
                
        return late
    
    async def get_assignment_summary(self, max_courses: int = 5) -> Dict[str, Any]:
        """
        Get a summary of important assignments across all courses
        Limits the amount of data retrieved to stay within token limits
        
        Args:
            max_courses: Maximum number of courses to check
            
        Returns:
            Summary of assignments organized by course
        """
        courses = await self.get_courses()
        
        if not courses:
            return {"summary": "No courses found"}
            
        # Limit number of courses to reduce token usage
        courses = courses[:max_courses]
        
        summary = {
            "courses": len(courses),
            "courses_checked": min(len(courses), max_courses),
            "late_assignments": [],
            "upcoming_assignments": []
        }
        
        # Gather data for each course, but limit to reduce token usage
        for course in courses:
            course_id = course.get("id")
            course_name = course.get("name")
            
            # Get late assignments
            late = await self.get_late_assignments(course_id)
            if late:
                for assignment in late:
                    summary["late_assignments"].append({
                        "course_name": course_name,
                        "course_id": course_id,
                        "assignment_name": assignment.get("name"),
                        "assignment_id": assignment.get("id"),
                        "due_date": assignment.get("due_at"),
                        "points_possible": assignment.get("points_possible")
                    })
            
            # Get upcoming assignments (due within 7 days to limit data)
            upcoming = await self.get_upcoming_assignments(course_id, days=7)
            if upcoming:
                for assignment in upcoming:
                    summary["upcoming_assignments"].append({
                        "course_name": course_name,
                        "course_id": course_id,
                        "assignment_name": assignment.get("name"),
                        "assignment_id": assignment.get("id"),
                        "due_date": assignment.get("due_at"),
                        "points_possible": assignment.get("points_possible")
                    })
        
        # Sort by due date
        summary["late_assignments"].sort(key=lambda x: x.get("due_date", ""))
        summary["upcoming_assignments"].sort(key=lambda x: x.get("due_date", ""))
        
        return summary 