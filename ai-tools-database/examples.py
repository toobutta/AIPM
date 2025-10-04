"""
Example tool definitions for populating the database
"""

EXAMPLE_TOOLS = {
    "weather": {
        "name": "get_weather",
        "description": "Get current weather information for a specific location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and state, e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit"
                }
            },
            "required": ["location"]
        },
        "category": "utilities",
        "tags": ["weather", "location", "temperature"],
        "examples": [
            {
                "name": "basic_weather",
                "description": "Get basic weather information",
                "input": {"location": "New York, NY"},
                "output": {"temperature": 72, "condition": "sunny", "humidity": 65}
            }
        ]
    },
    "search": {
        "name": "web_search",
        "description": "Search the web for information using a search engine",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query or keywords"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return",
                    "minimum": 1,
                    "maximum": 10,
                    "default": 5
                },
                "safe_search": {
                    "type": "boolean",
                    "description": "Enable safe search filtering",
                    "default": True
                }
            },
            "required": ["query"]
        },
        "category": "search",
        "tags": ["web", "search", "information", "internet"],
        "examples": [
            {
                "name": "basic_search",
                "description": "Search for current events",
                "input": {"query": "latest technology news", "num_results": 3},
                "output": [{"title": "Tech News", "url": "https://example.com", "snippet": "Latest tech updates"}]
            }
        ]
    },
    "database": {
        "name": "query_database",
        "description": "Execute SQL queries on a database",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "SQL query to execute"
                },
                "database": {
                    "type": "string",
                    "description": "Database name or connection string"
                },
                "read_only": {
                    "type": "boolean",
                    "description": "Restrict to read-only operations",
                    "default": True
                }
            },
            "required": ["query"]
        },
        "category": "data_access",
        "tags": ["database", "sql", "query", "data"],
        "examples": [
            {
                "name": "select_query",
                "description": "Select data from a table",
                "input": {
                    "query": "SELECT * FROM users WHERE active = true LIMIT 10",
                    "database": "myapp_db",
                    "read_only": True
                },
                "output": [{"id": 1, "name": "John", "email": "john@example.com"}]
            }
        ]
    },
    "calculator": {
        "name": "calculate",
        "description": "Perform mathematical calculations",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate"
                },
                "precision": {
                    "type": "integer",
                    "description": "Number of decimal places",
                    "minimum": 0,
                    "maximum": 10,
                    "default": 2
                }
            },
            "required": ["expression"]
        },
        "category": "calculation",
        "tags": ["math", "calculator", "arithmetic"],
        "examples": [
            {
                "name": "basic_math",
                "description": "Simple arithmetic calculation",
                "input": {"expression": "2 + 2 * 3", "precision": 0},
                "output": {"result": 8}
            }
        ]
    },
    "email": {
        "name": "send_email",
        "description": "Send an email message",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "Recipient email address"
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject"
                },
                "body": {
                    "type": "string",
                    "description": "Email body content"
                },
                "html": {
                    "type": "boolean",
                    "description": "Send as HTML email",
                    "default": False
                }
            },
            "required": ["to", "subject", "body"]
        },
        "category": "communication",
        "tags": ["email", "smtp", "messaging"],
        "examples": [
            {
                "name": "simple_email",
                "description": "Send a simple text email",
                "input": {
                    "to": "recipient@example.com",
                    "subject": "Hello World",
                    "body": "This is a test email",
                    "html": False
                },
                "output": {"message_id": "12345", "status": "sent"}
            }
        ]
    },
    "file_operations": {
        "name": "read_file",
        "description": "Read the contents of a file",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read"
                },
                "encoding": {
                    "type": "string",
                    "description": "File encoding",
                    "default": "utf-8"
                },
                "max_size": {
                    "type": "integer",
                    "description": "Maximum file size in bytes",
                    "minimum": 1,
                    "maximum": 10485760,
                    "default": 102400
                }
            },
            "required": ["file_path"]
        },
        "category": "file_system",
        "tags": ["file", "read", "filesystem"],
        "examples": [
            {
                "name": "read_text_file",
                "description": "Read a text file",
                "input": {
                    "file_path": "/path/to/file.txt",
                    "encoding": "utf-8"
                },
                "output": {"content": "File contents here", "size": 1024}
            }
        ]
    },
    "api_client": {
        "name": "make_api_request",
        "description": "Make HTTP API requests",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "API endpoint URL"
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                    "description": "HTTP method",
                    "default": "GET"
                },
                "headers": {
                    "type": "object",
                    "description": "Request headers"
                },
                "body": {
                    "type": "object",
                    "description": "Request body"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Request timeout in seconds",
                    "minimum": 1,
                    "maximum": 60,
                    "default": 30
                }
            },
            "required": ["url"]
        },
        "category": "api",
        "tags": ["http", "api", "rest", "web"],
        "examples": [
            {
                "name": "get_request",
                "description": "Make a GET request",
                "input": {
                    "url": "https://api.example.com/users",
                    "method": "GET",
                    "headers": {"Authorization": "Bearer token123"}
                },
                "output": {"status": 200, "data": {"users": []}}
            }
        ]
    },
    "data_analysis": {
        "name": "analyze_data",
        "description": "Analyze structured data and generate insights",
        "parameters": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "description": "Array of data objects to analyze"
                },
                "analysis_type": {
                    "type": "string",
                    "enum": ["summary", "statistics", "correlation", "trends"],
                    "description": "Type of analysis to perform",
                    "default": "summary"
                },
                "group_by": {
                    "type": "string",
                    "description": "Field to group analysis by"
                }
            },
            "required": ["data"]
        },
        "category": "data_access",
        "tags": ["analysis", "statistics", "insights", "data"],
        "examples": [
            {
                "name": "sales_analysis",
                "description": "Analyze sales data",
                "input": {
                    "data": [
                        {"product": "A", "sales": 100, "month": "Jan"},
                        {"product": "B", "sales": 150, "month": "Jan"},
                        {"product": "A", "sales": 120, "month": "Feb"}
                    ],
                    "analysis_type": "summary",
                    "group_by": "product"
                },
                "output": {"product_a": {"total": 220}, "product_b": {"total": 150}}
            }
        ]
    },
    "code_execution": {
        "name": "execute_code",
        "description": "Execute code in a safe sandbox environment",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Code to execute"
                },
                "language": {
                    "type": "string",
                    "enum": ["python", "javascript", "bash"],
                    "description": "Programming language",
                    "default": "python"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Execution timeout in seconds",
                    "minimum": 1,
                    "maximum": 30,
                    "default": 10
                }
            },
            "required": ["code"]
        },
        "category": "development",
        "tags": ["code", "execution", "programming", "sandbox"],
        "examples": [
            {
                "name": "python_script",
                "description": "Execute Python code",
                "input": {
                    "code": "print('Hello, World!')",
                    "language": "python",
                    "timeout": 5
                },
                "output": {"stdout": "Hello, World!\n", "exit_code": 0}
            }
        ]
    },
    "document_processing": {
        "name": "extract_text",
        "description": "Extract text from documents and images",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the document file"
                },
                "format": {
                    "type": "string",
                    "enum": ["pdf", "docx", "txt", "jpg", "png"],
                    "description": "Document format"
                },
                "language": {
                    "type": "string",
                    "description": "Document language",
                    "default": "en"
                }
            },
            "required": ["file_path", "format"]
        },
        "category": "utilities",
        "tags": ["ocr", "document", "text", "extraction"],
        "examples": [
            {
                "name": "pdf_extraction",
                "description": "Extract text from PDF",
                "input": {
                    "file_path": "/path/to/document.pdf",
                    "format": "pdf",
                    "language": "en"
                },
                "output": {"text": "Extracted text content", "pages": 5}
            }
        ]
    }
}

PROVIDER_EXAMPLES = {
    "claude_to_openai": {
        "source": {
            "name": "get_weather",
            "description": "Get current weather in a location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"]
                    }
                },
                "required": ["location"]
            }
        },
        "target": {
            "name": "get_weather",
            "description": "Get current weather in a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"]
                    }
                },
                "required": ["location"]
            }
        }
    },
    "openai_to_mistral": {
        "source": {
            "name": "web_search",
            "description": "Search the web",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        },
        "target": {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"}
                    },
                    "required": ["query"]
                }
            }
        }
    },
    "complex_example": {
        "source": {
            "name": "analyze_data",
            "description": "Analyze structured data",
            "input_schema": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "value": {"type": "number"},
                                "category": {"type": "string"}
                            }
                        }
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["mean", "median", "sum", "count"]
                    }
                },
                "required": ["data"]
            }
        },
        "target_openai": {
            "name": "analyze_data",
            "description": "Analyze structured data",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "value": {"type": "number"},
                                "category": {"type": "string"}
                            }
                        }
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["mean", "median", "sum", "count"]
                    }
                },
                "required": ["data"]
            }
        }
    }
}

VALIDATION_EXAMPLES = {
    "valid_claude": {
        "name": "get_weather",
        "description": "Get current weather information",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and state"
                }
            },
            "required": ["location"]
        }
    },
    "invalid_missing_required": {
        "name": "get_weather",
        "description": "Get current weather information"
        # Missing input_schema
    },
    "invalid_type": {
        "name": "get_weather",
        "description": "Get current weather information",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "invalid_type",  # Invalid type
                    "description": "City and state"
                }
            },
            "required": ["location"]
        }
    }
}