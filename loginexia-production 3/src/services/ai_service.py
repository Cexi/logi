import openai
import json
import re
from datetime import datetime
from flask import current_app
from src.models.organization import Organization

class AIService:
    def __init__(self):
        # OpenAI client is already configured via environment variables
        self.client = openai.OpenAI()
        
    def generate_sql_from_nl(self, natural_query, organization_id, schema_info=None):
        """Convert natural language to SQL query"""
        
        # Database schema for rider management
        default_schema = """
        Tables available:
        - riders: id, name, email, phone, status, cash_amount, battery_level, vehicle_type, city_id, created_at
        - shifts: id, rider_id, start_time, end_time, status, planned_start, actual_start
        - deliveries: id, rider_id, order_id, pickup_time, delivery_time, status, distance_km
        - companies: id, name, city_id, active_riders_count, total_deliveries_today
        - alerts: id, rider_id, alert_type, severity, status, created_at, resolved_at
        
        Important: Always filter by organization_id = '{organization_id}' for data isolation.
        """
        
        schema = schema_info or default_schema.format(organization_id=organization_id)
        
        prompt = f"""
        You are a SQL expert. Convert the following natural language query to SQL.
        
        Database Schema:
        {schema}
        
        Natural Language Query: {natural_query}
        
        Rules:
        1. Always include WHERE organization_id = '{organization_id}' for data isolation
        2. Use proper SQL syntax for PostgreSQL
        3. Return only the SQL query, no explanations
        4. Use appropriate JOINs when needed
        5. Handle date/time queries properly
        6. Use LIMIT for potentially large result sets
        
        SQL Query:
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a SQL expert that converts natural language to SQL queries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Basic SQL injection prevention
            sql_query = self._sanitize_sql(sql_query)
            
            return {
                'sql_query': sql_query,
                'natural_query': natural_query,
                'confidence': 'high',
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f"Failed to generate SQL: {str(e)}",
                'natural_query': natural_query,
                'generated_at': datetime.utcnow().isoformat()
            }
    
    def _sanitize_sql(self, sql_query):
        """Basic SQL sanitization"""
        # Remove dangerous SQL commands
        dangerous_patterns = [
            r'\bDROP\b', r'\bDELETE\b', r'\bUPDATE\b', r'\bINSERT\b',
            r'\bALTER\b', r'\bCREATE\b', r'\bTRUNCATE\b', r'\bEXEC\b'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, sql_query, re.IGNORECASE):
                raise ValueError(f"Potentially dangerous SQL operation detected: {pattern}")
        
        return sql_query
    
    def query_knowledge_base(self, question, organization_id, context_docs=None):
        """Answer questions using RAG (Retrieval Augmented Generation)"""
        
        # Default context about rider management
        default_context = """
        Loginexia is a rider management platform that integrates with Delivery Hero's APIs.
        
        Key features:
        - Real-time rider tracking and status monitoring
        - Automated alert system for cash thresholds, no-shows, battery levels
        - Performance analytics and KPI tracking
        - Support ticket management
        - AI-powered insights and recommendations
        
        Rider states include: AVAILABLE, BREAK, ENDING, LATE, NOT_WORKING, READY, STARTING, TEMP_NOT_WORKING, WORKING
        
        Common alerts:
        - Cash threshold: When rider has ≥€120 cash
        - No-show: When rider is late for shift
        - Battery low: When device battery <20%
        - Off-zone: When rider is outside designated area
        """
        
        context = context_docs or default_context
        
        prompt = f"""
        Context: {context}
        
        Question: {question}
        
        Please provide a helpful and accurate answer based on the context provided. 
        If the question is about specific data, mention that the user should check their dashboard or run a query.
        Keep the answer concise but informative.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for a rider management platform. Provide accurate and helpful answers based on the context provided."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            answer = response.choices[0].message.content.strip()
            
            return {
                'answer': answer,
                'question': question,
                'confidence': 'high',
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f"Failed to generate answer: {str(e)}",
                'question': question,
                'generated_at': datetime.utcnow().isoformat()
            }
    
    def generate_recommendations(self, rider_data, historical_patterns=None, recommendation_type='general'):
        """Generate AI-powered recommendations"""
        
        data_summary = self._summarize_rider_data(rider_data)
        
        prompts = {
            'general': f"""
            Based on this rider data: {data_summary}
            
            Provide 3-5 actionable recommendations to improve rider performance and operational efficiency.
            Focus on practical suggestions that can be implemented immediately.
            """,
            'scheduling': f"""
            Based on this rider data: {data_summary}
            
            Provide recommendations for optimal shift scheduling:
            1. Best times to schedule shifts based on demand patterns
            2. Rider availability optimization
            3. Workload balancing suggestions
            """,
            'performance': f"""
            Based on this rider data: {data_summary}
            
            Provide performance improvement recommendations:
            1. Identify underperforming areas
            2. Suggest training or support needs
            3. Recommend performance incentives
            """,
            'alerts': f"""
            Based on this rider data: {data_summary}
            
            Provide recommendations for alert management:
            1. Which alerts need immediate attention
            2. Preventive measures for common issues
            3. Escalation procedures
            """
        }
        
        prompt = prompts.get(recommendation_type, prompts['general'])
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in logistics and rider management. Provide practical, actionable recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=1000
            )
            
            recommendations_text = response.choices[0].message.content.strip()
            recommendations = self._parse_recommendations(recommendations_text)
            
            return {
                'recommendations': recommendations,
                'type': recommendation_type,
                'confidence': 'high',
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f"Failed to generate recommendations: {str(e)}",
                'type': recommendation_type,
                'generated_at': datetime.utcnow().isoformat()
            }
    
    def _summarize_rider_data(self, rider_data):
        """Summarize rider data for AI processing"""
        if isinstance(rider_data, dict):
            return json.dumps(rider_data, indent=2)
        elif isinstance(rider_data, list):
            summary = {
                'total_riders': len(rider_data),
                'active_riders': len([r for r in rider_data if r.get('status') == 'WORKING']),
                'available_riders': len([r for r in rider_data if r.get('status') == 'AVAILABLE']),
                'riders_on_break': len([r for r in rider_data if r.get('status') == 'BREAK']),
                'sample_rider': rider_data[0] if rider_data else None
            }
            return json.dumps(summary, indent=2)
        else:
            return str(rider_data)
    
    def _parse_recommendations(self, recommendations_text):
        """Parse recommendations text into structured format"""
        lines = recommendations_text.split('\n')
        recommendations = []
        
        current_rec = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if it's a numbered recommendation
            if re.match(r'^\d+\.', line):
                if current_rec:
                    recommendations.append(current_rec)
                current_rec = {
                    'title': re.sub(r'^\d+\.\s*', '', line),
                    'description': '',
                    'priority': 'medium',
                    'category': 'operational'
                }
            elif current_rec and line.startswith('-'):
                current_rec['description'] += line + '\n'
            elif current_rec:
                current_rec['description'] += line + ' '
        
        if current_rec:
            recommendations.append(current_rec)
        
        # If parsing failed, create a single recommendation with the full text
        if not recommendations:
            recommendations = [{
                'title': 'AI Recommendations',
                'description': recommendations_text,
                'priority': 'medium',
                'category': 'general'
            }]
        
        return recommendations
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of support tickets or feedback"""
        prompt = f"""
        Analyze the sentiment of the following text and categorize it:
        
        Text: {text}
        
        Provide:
        1. Sentiment: positive, negative, or neutral
        2. Confidence: high, medium, or low
        3. Key emotions detected
        4. Urgency level: low, medium, high, urgent
        
        Format as JSON.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in sentiment analysis. Provide accurate sentiment analysis in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=300
            )
            
            result = response.choices[0].message.content.strip()
            
            # Try to parse as JSON, fallback to structured response
            try:
                return json.loads(result)
            except:
                return {
                    'sentiment': 'neutral',
                    'confidence': 'medium',
                    'emotions': ['unknown'],
                    'urgency': 'medium',
                    'raw_analysis': result
                }
                
        except Exception as e:
            return {
                'error': f"Failed to analyze sentiment: {str(e)}",
                'sentiment': 'neutral',
                'confidence': 'low'
            }

