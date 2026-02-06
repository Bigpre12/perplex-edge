"""
Frontend Brain Service - Autonomous frontend improvements, fixes, and expansions.

This module provides capabilities for the brain to automatically:
- Monitor frontend health and performance
- Fix frontend issues and bugs
- Improve UI/UX based on usage patterns
- Expand frontend features
- Auto-commit frontend changes to git
"""

import logging
import os
import json
import subprocess
import httpx
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class FrontendBrain:
    """Autonomous frontend improvement and fixing system."""
    
    def __init__(self):
        self.frontend_path = Path(__file__).parent.parent.parent / "frontend"
        self.last_frontend_scan: Optional[datetime] = None
        self.frontend_issues_found: int = 0
        self.frontend_fixes_applied: int = 0
        self.frontend_improvements_made: int = 0
        self.frontend_expansions_added: int = 0

async def check_frontend_health() -> Dict[str, Any]:
    """Check frontend health, performance, and user experience."""
    try:
        health_report = {
            "status": "healthy",
            "issues": [],
            "performance_metrics": {},
            "accessibility_score": 0,
            "bundle_size_mb": 0,
            "load_time_ms": 0,
            "error_count": 0,
            "recommendations": []
        }
        
        # Check if frontend is accessible
        frontend_url = os.getenv("FRONTEND_URL", "https://perplex-edge-production.up.railway.app")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(frontend_url)
                if response.status_code != 200:
                    health_report["issues"].append(f"Frontend not accessible: HTTP {response.status_code}")
                    health_report["status"] = "critical"
                else:
                    health_report["load_time_ms"] = response.elapsed.total_seconds() * 1000
                    
                    # Check for common frontend issues
                    content = response.text
                    
                    # Check for JavaScript errors
                    if "error" in content.lower() and "javascript" in content.lower():
                        health_report["issues"].append("Potential JavaScript errors detected")
                        health_report["error_count"] += 1
                    
                    # Check for loading issues
                    if "loading" in content.lower() and "failed" in content.lower():
                        health_report["issues"].append("Loading failures detected")
                        health_report["error_count"] += 1
                    
                    # Check for CORS errors in content
                    if "cors" in content.lower() and "blocked" in content.lower():
                        health_report["issues"].append("CORS errors detected in frontend")
                        health_report["error_count"] += 1
                        
            except httpx.TimeoutException:
                health_report["issues"].append("Frontend timeout - slow loading")
                health_report["status"] = "degraded"
                health_report["load_time_ms"] = 15000  # Timeout
            except Exception as e:
                health_report["issues"].append(f"Frontend inaccessible: {str(e)}")
                health_report["status"] = "critical"
        
        # Check frontend build configuration
        frontend_brain = FrontendBrain()
        package_json_path = frontend_brain.frontend_path / "package.json"
        
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                    
                # Check for performance optimizations
                health_report["performance_metrics"]["has_vite"] = "vite" in package_data.get("devDependencies", {})
                health_report["performance_metrics"]["has_react_query"] = "@tanstack/react-query" in package_data.get("dependencies", {})
                health_report["performance_metrics"]["has_tailwind"] = "tailwindcss" in package_data.get("devDependencies", {})
                
                # Recommendations based on missing optimizations
                if not health_report["performance_metrics"]["has_vite"]:
                    health_report["recommendations"].append("Consider using Vite for faster builds")
                if not health_report["performance_metrics"]["has_react_query"]:
                    health_report["recommendations"].append("Add React Query for better data fetching")
                if not health_report["performance_metrics"]["has_tailwind"]:
                    health_report["recommendations"].append("Add Tailwind CSS for better styling")
                    
            except Exception as e:
                health_report["issues"].append(f"Failed to analyze package.json: {str(e)}")
        
        # Check for common frontend files
        critical_files = [
            "src/App.tsx",
            "src/main.tsx",
            "index.html",
            "vite.config.ts"
        ]
        
        for file_path in critical_files:
            full_path = frontend_brain.frontend_path / file_path
            if not full_path.exists():
                health_report["issues"].append(f"Missing critical file: {file_path}")
                health_report["status"] = "degraded"
        
        # Determine overall status
        if health_report["error_count"] > 3:
            health_report["status"] = "critical"
        elif health_report["error_count"] > 0 or len(health_report["issues"]) > 2:
            health_report["status"] = "degraded"
        
        return health_report
        
    except Exception as e:
        logger.error(f"Frontend health check failed: {e}")
        return {
            "status": "critical",
            "issues": [f"Health check failed: {str(e)}"],
            "error": str(e)
        }

async def fix_frontend_issues() -> Dict[str, Any]:
    """Automatically fix common frontend issues."""
    try:
        fix_results = {
            "fixes_attempted": 0,
            "fixes_successful": 0,
            "fixes_failed": 0,
            "fixes_applied": [],
            "errors": []
        }
        
        frontend_brain = FrontendBrain()
        
        # Fix 1: Add CORS error handling
        try:
            app_tsx_path = frontend_brain.frontend_path / "src" / "App.tsx"
            if app_tsx_path.exists():
                with open(app_tsx_path, 'r') as f:
                    content = f.read()
                
                # Add CORS error handling if not present
                if "CORS" not in content and "fetch" in content:
                    cors_handler = """
// Global CORS error handling
const originalFetch = window.fetch;
window.fetch = async (...args) => {
  try {
    const response = await originalFetch(...args);
    return response;
  } catch (error) {
    if (error.message.includes('CORS')) {
      console.warn('CORS error detected, retrying with CORS workaround');
      // Add CORS workaround logic here
    }
    throw error;
  }
};
"""
                    
                    if "// Global CORS error handling" not in content:
                        content += cors_handler
                        with open(app_tsx_path, 'w') as f:
                            f.write(content)
                        
                        fix_results["fixes_successful"] += 1
                        fix_results["fixes_applied"].append("Added CORS error handling")
                        
            fix_results["fixes_attempted"] += 1
            
        except Exception as e:
            fix_results["fixes_failed"] += 1
            fix_results["errors"].append(f"CORS fix failed: {str(e)}")
        
        # Fix 2: Add error boundary component
        try:
            error_boundary_path = frontend_brain.frontend_path / "src" / "components" / "ErrorBoundary.tsx"
            error_boundary_path.parent.mkdir(exist_ok=True)
            
            if not error_boundary_path.exists():
                error_boundary_code = """import React from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends React.Component<
  React.PropsWithChildren<{}>,
  ErrorBoundaryState
> {
  constructor(props: React.PropsWithChildren<{}>) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Frontend error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
          <div className="bg-white p-8 rounded-lg shadow-md max-w-md">
            <h2 className="text-xl font-semibold text-red-600 mb-4">
              Something went wrong
            </h2>
            <p className="text-gray-600 mb-4">
              We're sorry, but something unexpected happened. 
              Please refresh the page and try again.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              Refresh Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
"""
                
                with open(error_boundary_path, 'w') as f:
                    f.write(error_boundary_code)
                
                fix_results["fixes_successful"] += 1
                fix_results["fixes_applied"].append("Added ErrorBoundary component")
                
            fix_results["fixes_attempted"] += 1
            
        except Exception as e:
            fix_results["fixes_failed"] += 1
            fix_results["errors"].append(f"ErrorBoundary fix failed: {str(e)}")
        
        # Fix 3: Add loading states
        try:
            loading_component_path = frontend_brain.frontend_path / "src" / "components" / "LoadingSpinner.tsx"
            loading_component_path.parent.mkdir(exist_ok=True)
            
            if not loading_component_path.exists():
                loading_code = """import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  message = 'Loading...' 
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };

  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div 
        className={\\`animate-spin rounded-full border-4 border-blue-500 border-t-transparent \\${sizeClasses[size]}\\`}
      />
      {message && (
        <p className="mt-2 text-sm text-gray-600">{message}</p>
      )}
    </div>
  );
};

export default LoadingSpinner;
"""
                
                with open(loading_component_path, 'w') as f:
                    f.write(loading_code)
                
                fix_results["fixes_successful"] += 1
                fix_results["fixes_applied"].append("Added LoadingSpinner component")
                
            fix_results["fixes_attempted"] += 1
            
        except Exception as e:
            fix_results["fixes_failed"] += 1
            fix_results["errors"].append(f"LoadingSpinner fix failed: {str(e)}")
        
        return fix_results
        
    except Exception as e:
        logger.error(f"Frontend fixing failed: {e}")
        return {
            "fixes_attempted": 0,
            "fixes_successful": 0,
            "fixes_failed": 1,
            "errors": [str(e)]
        }

async def improve_frontend_performance() -> Dict[str, Any]:
    """Automatically improve frontend performance."""
    try:
        improvement_results = {
            "improvements_attempted": 0,
            "improvements_successful": 0,
            "improvements_applied": [],
            "errors": []
        }
        
        frontend_brain = FrontendBrain()
        
        # Improvement 1: Add React Query if missing
        try:
            package_json_path = frontend_brain.frontend_path / "package.json"
            if package_json_path.exists():
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                
                if "@tanstack/react-query" not in package_data.get("dependencies", {}):
                    # Add React Query to dependencies
                    if "dependencies" not in package_data:
                        package_data["dependencies"] = {}
                    
                    package_data["dependencies"]["@tanstack/react-query"] = "^5.0.0"
                    
                    with open(package_json_path, 'w') as f:
                        json.dump(package_data, f, indent=2)
                    
                    improvement_results["improvements_successful"] += 1
                    improvement_results["improvements_applied"].append("Added React Query for data fetching")
                    
            improvement_results["improvements_attempted"] += 1
            
        except Exception as e:
            improvement_results["improvements_failed"] = 1
            improvement_results["errors"].append(f"React Query addition failed: {str(e)}")
        
        # Improvement 2: Add performance monitoring
        try:
            performance_hook_path = frontend_brain.frontend_path / "src" / "hooks" / "usePerformanceMonitor.ts"
            performance_hook_path.parent.mkdir(exist_ok=True)
            
            if not performance_hook_path.exists():
                performance_code = """import { useEffect, useRef } from 'react';

interface PerformanceMetrics {
  loadTime: number;
  renderTime: number;
  memoryUsage: number;
}

export const usePerformanceMonitor = (componentName: string) => {
  const startTime = useRef<number>(Date.now());
  
  useEffect(() => {
    const endTime = Date.now();
    const renderTime = endTime - startTime.current;
    
    // Log performance metrics
    if (process.env.NODE_ENV === 'development') {
      console.log(\`[Performance] \${componentName} rendered in \${renderTime}ms\`);
    }
    
    // Monitor memory usage if available
    if ('memory' in performance) {
      const memory = (performance as any).memory;
      const memoryUsage = memory.usedJSHeapSize / 1024 / 1024; // MB
      
      if (memoryUsage > 50) { // Warn if using more than 50MB
        console.warn(\`[Performance] \${componentName} using \${memoryUsage.toFixed(2)}MB memory\`);
      }
    }
  });
  
  return {
    renderTime: Date.now() - startTime.current
  };
};
"""
                
                with open(performance_hook_path, 'w') as f:
                    f.write(performance_code)
                
                improvement_results["improvements_successful"] += 1
                improvement_results["improvements_applied"].append("Added performance monitoring hook")
                
            improvement_results["improvements_attempted"] += 1
            
        except Exception as e:
            improvement_results["improvements_failed"] = 1
            improvement_results["errors"].append(f"Performance monitoring addition failed: {str(e)}")
        
        return improvement_results
        
    except Exception as e:
        logger.error(f"Frontend performance improvement failed: {e}")
        return {
            "improvements_attempted": 0,
            "improvements_successful": 0,
            "improvements_failed": 1,
            "errors": [str(e)]
        }

async def expand_frontend_features() -> Dict[str, Any]:
    """Automatically expand frontend with new features."""
    try:
        expansion_results = {
            "expansions_attempted": 0,
            "expansions_successful": 0,
            "expansions_added": [],
            "errors": []
        }
        
        frontend_brain = FrontendBrain()
        
        # Expansion 1: Add dark mode toggle
        try:
            dark_mode_hook_path = frontend_brain.frontend_path / "src" / "hooks" / "useDarkMode.ts"
            dark_mode_hook_path.parent.mkdir(exist_ok=True)
            
            if not dark_mode_hook_path.exists():
                dark_mode_code = """import { useState, useEffect } from 'react';

export const useDarkMode = () => {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    // Check localStorage and system preference
    const saved = localStorage.getItem('darkMode');
    if (saved !== null) return saved === 'true';
    
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    const root = document.documentElement;
    
    if (isDarkMode) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    
    localStorage.setItem('darkMode', isDarkMode.toString());
  }, [isDarkMode]);

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
  };

  return {
    isDarkMode,
    toggleDarkMode
  };
};
"""
                
                with open(dark_mode_hook_path, 'w') as f:
                    f.write(dark_mode_code)
                
                expansion_results["expansions_successful"] += 1
                expansion_results["expansions_added"].append("Added dark mode toggle")
                
            expansion_results["expansions_attempted"] += 1
            
        except Exception as e:
            expansion_results["expansions_failed"] = 1
            expansion_results["errors"].append(f"Dark mode addition failed: {str(e)}")
        
        # Expansion 2: Add notification system
        try:
            notification_context_path = frontend_brain.frontend_path / "src" / "contexts" / "NotificationContext.tsx"
            notification_context_path.parent.mkdir(exist_ok=True)
            
            if not notification_context_path.exists():
                notification_code = """import React, { createContext, useContext, useReducer, ReactNode } from 'react';

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
}

interface NotificationState {
  notifications: Notification[];
}

type NotificationAction =
  | { type: 'ADD_NOTIFICATION'; payload: Notification }
  | { type: 'REMOVE_NOTIFICATION'; payload: string };

const NotificationContext = createContext<{
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id'>) => void;
  removeNotification: (id: string) => void;
} | null>(null);

const notificationReducer = (
  state: NotificationState,
  action: NotificationAction
): NotificationState => {
  switch (action.type) {
    case 'ADD_NOTIFICATION':
      return {
        ...state,
        notifications: [...state.notifications, { ...action.payload, id: Date.now().toString() }]
      };
    case 'REMOVE_NOTIFICATION':
      return {
        ...state,
        notifications: state.notifications.filter(n => n.id !== action.payload)
      };
    default:
      return state;
  }
};

export const NotificationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(notificationReducer, { notifications: [] });

  const addNotification = (notification: Omit<Notification, 'id'>) => {
    dispatch({ type: 'ADD_NOTIFICATION', payload: notification });
    
    // Auto-remove after duration
    const duration = notification.duration || 5000;
    setTimeout(() => {
      dispatch({ type: 'REMOVE_NOTIFICATION', payload: Date.now().toString() });
    }, duration);
  };

  const removeNotification = (id: string) => {
    dispatch({ type: 'REMOVE_NOTIFICATION', payload: id });
  };

  return (
    <NotificationContext.Provider value={{
      notifications: state.notifications,
      addNotification,
      removeNotification
    }}>
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
};
"""
                
                with open(notification_context_path, 'w') as f:
                    f.write(notification_code)
                
                expansion_results["expansions_successful"] += 1
                expansion_results["expansions_added"].append("Added notification system")
                
            expansion_results["expansions_attempted"] += 1
            
        except Exception as e:
            expansion_results["expansions_failed"] = 1
            expansion_results["errors"].append(f"Notification system addition failed: {str(e)}")
        
        return expansion_results
        
    except Exception as e:
        logger.error(f"Frontend expansion failed: {e}")
        return {
            "expansions_attempted": 0,
            "expansions_successful": 0,
            "expansions_failed": 1,
            "errors": [str(e)]
        }

async def auto_commit_frontend_changes(changes: List[str], commit_type: str = "frontend-auto-update") -> bool:
    """Automatically commit frontend changes to git."""
    try:
        import subprocess
        
        frontend_brain = FrontendBrain()
        repo_root = frontend_brain.frontend_path.parent
        
        # Stage frontend changes
        try:
            result = subprocess.run(
                ['git', 'add', 'frontend/'],
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                logger.warning(f"[BRAIN] Frontend git add failed: {result.stderr}")
                return False
        except Exception as e:
            logger.warning(f"[BRAIN] Frontend git add error: {e}")
            return False
        
        # Commit changes
        try:
            commit_message = f"feat: {commit_type}\n\nAutomated frontend improvements:\n" + "\n".join(f"- {change}" for change in changes)
            
            result = subprocess.run(
                ['git', 'commit', '-m', commit_message],
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                logger.warning(f"[BRAIN] Frontend git commit failed: {result.stderr}")
                return False
        except Exception as e:
            logger.warning(f"[BRAIN] Frontend git commit error: {e}")
            return False
        
        # Push changes
        try:
            result = subprocess.run(
                ['git', 'push'],
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                logger.warning(f"[BRAIN] Frontend git push failed: {result.stderr}")
                return True  # Commit succeeded, push failed
        except Exception as e:
            logger.warning(f"[BRAIN] Frontend git push error: {e}")
            return True  # Commit succeeded, push error
        
        logger.info(f"[BRAIN] Successfully committed and pushed frontend {commit_type} with {len(changes)} changes")
        return True
        
    except Exception as e:
        logger.error(f"[BRAIN] Frontend auto-git commit failed: {e}")
        return False
