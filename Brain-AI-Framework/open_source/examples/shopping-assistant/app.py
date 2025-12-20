"""
Shopping Assistant - Brain AI Framework Example
A comprehensive shopping assistant that helps customers with personalized recommendations,
product search, price comparison, and intelligent retail assistance.
"""

import json
import asyncio
import uvicorn
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
import sys
import os
import math
import statistics
import random

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from loguru import logger
from dataclasses import dataclass
from enum import Enum

# Import shared components
from shared.brain_ai_integration import BrainAIIntegration, BrainAIMemory
from shared.demo_data import DemoDataGenerator
from shared.web_components import WebComponents

# Configure logging
logger.add("logs/shopping_assistant.log", rotation="10 MB", level="INFO")

class ProductCategory(Enum):
    """Product category enumeration"""
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    HOME_GARDEN = "home_garden"
    BOOKS = "books"
    HEALTH_BEAUTY = "health_beauty"
    SPORTS = "sports"
    AUTOMOTIVE = "automotive"
    TOYS = "toys"
    GROCERY = "grocery"
    OFFICE = "office"

class ProductCondition(Enum):
    """Product condition enumeration"""
    NEW = "new"
    LIKE_NEW = "like_new"
    GOOD = "good"
    FAIR = "fair"
    REFURBISHED = "refurbished"

class PriceType(Enum):
    """Price type enumeration"""
    REGULAR = "regular"
    SALE = "sale"
    CLEARANCE = "clearance"
    BUNDLE = "bundle"
    SUBSCRIPTION = "subscription"

class RecommendationType(Enum):
    """Recommendation type enumeration"""
    SIMILAR_PRODUCTS = "similar_products"
    COMPLEMENTARY = "complementary"
    FREQUENTLY_BOUGHT = "frequently_bought"
    PERSONALIZED = "personalized"
    TRENDING = "trending"
    PRICE_DROP = "price_drop"

class UserIntent(Enum):
    """User intent enumeration"""
    BUY_NOW = "buy_now"
    BROWSE = "browse"
    COMPARE = "compare"
    SEARCH = "search"
    SUPPORT = "support"
    REVIEW = "review"

@dataclass
class PriceHistory:
    """Product price history"""
    date: datetime
    price: float
    price_type: PriceType
    discount_percentage: float

@dataclass
class ProductRating:
    """Product rating data"""
    average_rating: float
    total_reviews: int
    rating_distribution: Dict[int, int]  # 5-star: count, 4-star: count, etc.

class Product(BaseModel):
    """Product model"""
    product_id: str
    name: str
    description: str
    category: ProductCategory
    brand: str
    price: float
    original_price: Optional[float]
    condition: ProductCondition
    availability: str
    stock_quantity: int
    specifications: Dict[str, Any]
    features: List[str]
    tags: List[str]
    images: List[str]
    seller_info: Dict[str, str]
    ratings: ProductRating
    price_history: List[PriceHistory]
    created_date: datetime

class UserProfile(BaseModel):
    """User profile model"""
    user_id: str
    name: str
    email: str
    preferences: Dict[str, Any]
    purchase_history: List[str]
    browsing_history: List[str]
    wishlist: List[str]
    demographics: Dict[str, Any]
    created_date: datetime
    last_active: datetime

class ShoppingSession(BaseModel):
    """Shopping session model"""
    session_id: str
    user_id: str
    start_time: datetime
    intent: UserIntent
    current_products: List[str]
    search_queries: List[str]
    interactions: List[Dict]
    cart_items: List[Dict]
    total_value: float

class Recommendation(BaseModel):
    """Product recommendation model"""
    recommendation_id: str
    user_id: str
    product_id: str
    recommendation_type: RecommendationType
    confidence_score: float
    reasoning: str
    metadata: Dict[str, Any]
    created_date: datetime

class ShoppingInsight(BaseModel):
    """Shopping insight model"""
    insight_id: str
    user_id: str
    insight_type: str
    title: str
    description: str
    impact_level: str
    action_items: List[str]
    potential_savings: Dict[str, float]
    confidence_score: float
    timestamp: datetime

class ShoppingAssistantAI:
    """Main shopping assistant AI engine"""
    
    def __init__(self, brain_ai: BrainAIIntegration):
        self.brain_ai = brain_ai
        self.demo_data = DemoDataGenerator()
        self.web_components = WebComponents()
        self.products: Dict[str, Product] = {}
        self.user_profiles: Dict[str, UserProfile] = {}
        self.shopping_sessions: Dict[str, ShoppingSession] = {}
        self.recommendations: Dict[str, Recommendation] = {}
        self.shopping_insights: Dict[str, ShoppingInsight] = {}
        
        # Shopping configuration
        self.shopping_config = {
            "max_recommendations": 10,
            "similarity_threshold": 0.7,
            "price_tolerance": 0.1,
            "stock_threshold": 5,
            "rating_threshold": 3.5
        }
        
        # Product categories with subcategories
        self.category_hierarchy = self._initialize_category_hierarchy()
        
        # Initialize demo data
        self._initialize_demo_data()
    
    def _initialize_category_hierarchy(self) -> Dict:
        """Initialize product category hierarchy"""
        return {
            ProductCategory.ELECTRONICS: ["smartphones", "laptops", "tablets", "headphones", "cameras"],
            ProductCategory.CLOTHING: ["men", "women", "kids", "shoes", "accessories"],
            ProductCategory.HOME_GARDEN: ["furniture", "decor", "kitchen", "bedding", "garden"],
            ProductCategory.BOOKS: ["fiction", "non-fiction", "textbooks", "children", "comics"],
            ProductCategory.HEALTH_BEAUTY: ["skincare", "makeup", "supplements", "fitness", "personal_care"],
            ProductCategory.SPORTS: ["equipment", "apparel", "footwear", "outdoor", "fitness"],
            ProductCategory.AUTOMOTIVE: ["parts", "accessories", "tools", "maintenance", "electronics"],
            ProductCategory.TOYS: ["educational", "outdoor", "electronic", "board_games", "collectibles"],
            ProductCategory.GROCERY: ["fresh", "pantry", "beverages", "snacks", "organic"],
            ProductCategory.OFFICE: ["supplies", "furniture", "technology", "organization", "presentation"]
        }
    
    def _initialize_demo_data(self):
        """Initialize with demo data"""
        # Generate demo products
        for i in range(500):
            product = self.demo_data.generate_product_catalog(
                product_id=f"PROD_{i+1:04d}",
                category=random.choice(list(ProductCategory)),
                condition=random.choice(list(ProductCondition))
            )
            self.products[product.product_id] = product
        
        # Generate demo user profiles
        for i in range(100):
            user = self.demo_data.generate_user_profile(
                user_id=f"USER_{i+1:03d}",
                product_ids=list(self.products.keys())
            )
            self.user_profiles[user.user_id] = user
        
        # Generate demo shopping sessions
        for i in range(200):
            session = self.demo_data.generate_shopping_session(
                session_id=f"SESSION_{i+1:03d}",
                user_ids=list(self.user_profiles.keys()),
                product_ids=list(self.products.keys())
            )
            self.shopping_sessions[session.session_id] = session
        
        # Generate demo recommendations
        self._generate_recommendations()
        
        # Generate demo shopping insights
        self._generate_shopping_insights()
        
        logger.info(f"Initialized demo data: {len(self.products)} products, "
                   f"{len(self.user_profiles)} users, {len(self.shopping_sessions)} sessions")
    
    def _generate_recommendations(self):
        """Generate product recommendations"""
        for user_id in list(self.user_profiles.keys())[:50]:  # Generate for 50 users
            user = self.user_profiles[user_id]
            purchase_history = user.purchase_history
            
            # Generate personalized recommendations
            for _ in range(random.randint(3, 8)):
                product_id = random.choice(list(self.products.keys()))
                
                recommendation = Recommendation(
                    recommendation_id=f"REC_{len(self.recommendations)+1:04d}",
                    user_id=user_id,
                    product_id=product_id,
                    recommendation_type=random.choice(list(RecommendationType)),
                    confidence_score=random.uniform(0.6, 0.95),
                    reasoning=self._generate_recommendation_reasoning(product_id, user),
                    metadata=self._generate_recommendation_metadata(product_id, user),
                    created_date=datetime.now() - timedelta(hours=random.randint(1, 72))
                )
                
                self.recommendations[recommendation.recommendation_id] = recommendation
    
    def _generate_recommendation_reasoning(self, product_id: str, user: UserProfile) -> str:
        """Generate recommendation reasoning"""
        product = self.products[product_id]
        
        reasoning_templates = [
            f"Based on your interest in {product.category.value} products",
            f"Similar to your previous purchase: {random.choice(user.purchase_history)}",
            f"Trending in {product.category.value} category",
            f"Matches your preferences for {product.brand} products",
            f"Complements items in your cart",
            f"Highly rated by customers with similar preferences",
            f"Price drop alert for this product",
            f"Frequently bought together with your interests"
        ]
        
        return random.choice(reasoning_templates)
    
    def _generate_recommendation_metadata(self, product_id: str, user: UserProfile) -> Dict[str, Any]:
        """Generate recommendation metadata"""
        product = self.products[product_id]
        
        return {
            "similarity_score": random.uniform(0.6, 0.95),
            "price_competitiveness": random.uniform(0.7, 1.0),
            "availability": product.availability,
            "rating": product.ratings.average_rating,
            "category_match": random.choice([True, True, False]),
            "budget_match": random.choice([True, True, False])
        }
    
    def _generate_shopping_insights(self):
        """Generate shopping insights"""
        insight_types = [
            "spending_patterns", "category_preferences", "price_sensitivity",
            "seasonal_trends", "brand_loyalty", "cart_abandonment", "purchase_frequency"
        ]
        
        for user_id in list(self.user_profiles.keys())[:30]:  # Generate for 30 users
            insight_type = random.choice(insight_types)
            
            insight = ShoppingInsight(
                insight_id=f"INSIGHT_{len(self.shopping_insights)+1:03d}",
                user_id=user_id,
                insight_type=insight_type,
                title=self._generate_insight_title(insight_type),
                description=self._generate_insight_description(insight_type),
                impact_level=random.choice(["low", "medium", "high"]),
                action_items=self._generate_action_items(insight_type),
                potential_savings=self._generate_potential_savings(insight_type),
                confidence_score=random.uniform(0.7, 0.9),
                timestamp=datetime.now() - timedelta(hours=random.randint(1, 168))
            )
            
            self.shopping_insights[insight.insight_id] = insight
    
    def _generate_insight_title(self, insight_type: str) -> str:
        """Generate insight title"""
        titles = {
            "spending_patterns": "Spending Pattern Analysis",
            "category_preferences": "Category Preference Insights",
            "price_sensitivity": "Price Sensitivity Analysis",
            "seasonal_trends": "Seasonal Shopping Trends",
            "brand_loyalty": "Brand Loyalty Assessment",
            "cart_abandonment": "Cart Abandonment Factors",
            "purchase_frequency": "Purchase Frequency Optimization"
        }
        return titles.get(insight_type, "Shopping Insight Available")
    
    def _generate_insight_description(self, insight_type: str) -> str:
        """Generate insight description"""
        descriptions = {
            "spending_patterns": "Your spending shows consistent patterns with opportunities for better budgeting.",
            "category_preferences": "You have strong preferences in specific product categories.",
            "price_sensitivity": "Analysis shows you are price-conscious with specific sensitivity ranges.",
            "seasonal_trends": "Your shopping patterns align with seasonal buying behaviors.",
            "brand_loyalty": "You show strong loyalty to specific brands with crossover potential.",
            "cart_abandonment": "Common factors causing cart abandonment in your shopping journey.",
            "purchase_frequency": "Optimal purchase timing based on your buying patterns."
        }
        return descriptions.get(insight_type, "Shopping behavior analysis completed.")
    
    def _generate_action_items(self, insight_type: str) -> List[str]:
        """Generate action items based on insight type"""
        actions_map = {
            "spending_patterns": [
                "Set monthly spending budget",
                "Track expenses by category",
                "Review high-impact purchases",
                "Consider bulk buying for regular items"
            ],
            "category_preferences": [
                "Follow favorite brands for new releases",
                "Set up category-specific alerts",
                "Explore complementary categories",
                "Compare similar category products"
            ],
            "price_sensitivity": [
                "Set price drop alerts",
                "Compare prices across retailers",
                "Consider waiting for sales",
                "Look for bulk discounts"
            ],
            "seasonal_trends": [
                "Plan purchases around seasonal sales",
                "Stock up on seasonal items early",
                "Consider off-season buying",
                "Track seasonal price patterns"
            ],
            "brand_loyalty": [
                "Join brand loyalty programs",
                "Follow brand social media",
                "Consider brand alternatives",
                "Explore brand collaborations"
            ],
            "cart_abandonment": [
                "Complete checkout process quickly",
                "Save items for later purchase",
                "Compare final total before checkout",
                "Use saved payment methods"
            ],
            "purchase_frequency": [
                "Set reorder reminders",
                "Consider subscription options",
                "Plan bulk purchases",
                "Track consumption patterns"
            ]
        }
        
        return random.sample(actions_map.get(insight_type, []), random.randint(1, 3))
    
    def _generate_potential_savings(self, insight_type: str) -> Dict[str, float]:
        """Generate potential savings from insights"""
        savings_map = {
            "spending_patterns": {"monthly_savings": random.uniform(25, 100), "annual_savings": random.uniform(300, 1200)},
            "category_preferences": {"opportunity_cost": random.uniform(50, 200), "savings": random.uniform(20, 80)},
            "price_sensitivity": {"price_optimization": random.uniform(100, 300), "savings": random.uniform(50, 150)},
            "seasonal_trends": {"seasonal_savings": random.uniform(200, 500), "timing_savings": random.uniform(100, 250)},
            "brand_loyalty": {"loyalty_benefits": random.uniform(75, 200), "cross_selling": random.uniform(50, 150)},
            "cart_abandonment": {"recovery_potential": random.uniform(150, 400), "conversion_improvement": random.uniform(25, 75)},
            "purchase_frequency": {"frequency_optimization": random.uniform(100, 300), "efficiency_savings": random.uniform(50, 125)}
        }
        
        return savings_map.get(insight_type, {"potential_savings": random.uniform(25, 100)})
    
    async def generate_recommendations(self, user_id: str, context: Dict = None) -> List[Recommendation]:
        """Generate personalized recommendations using Brain AI"""
        try:
            user = self.user_profiles.get(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Prepare recommendation context
            recommendation_context = {
                "user_profile": user.dict(),
                "purchase_history": [self.products[pid].dict() for pid in user.purchase_history if pid in self.products],
                "browsing_history": [self.products[pid].dict() for pid in user.browsing_history if pid in self.products],
                "current_session": context,
                "market_trends": self._get_market_trends(),
                "similar_users": self._get_similar_users(user)
            }
            
            # Use Brain AI to generate recommendations
            ai_recommendations = await self.brain_ai.generate_product_recommendations(recommendation_context)
            
            # Generate recommendations based on different strategies
            recommendations = []
            
            # 1. Similar products to purchase history
            similar_products = self._find_similar_products(user.purchase_history, limit=3)
            for product_id in similar_products:
                rec = Recommendation(
                    recommendation_id=f"REC_{len(self.recommendations)+1:04d}",
                    user_id=user_id,
                    product_id=product_id,
                    recommendation_type=RecommendationType.SIMILAR_PRODUCTS,
                    confidence_score=random.uniform(0.7, 0.9),
                    reasoning=f"Similar to your previous purchase: {random.choice(user.purchase_history)}",
                    metadata={"similarity": random.uniform(0.7, 0.95)},
                    created_date=datetime.now()
                )
                recommendations.append(rec)
                self.recommendations[rec.recommendation_id] = rec
            
            # 2. Complementary products
            complementary_products = self._find_complementary_products(user.purchase_history, limit=3)
            for product_id in complementary_products:
                rec = Recommendation(
                    recommendation_id=f"REC_{len(self.recommendations)+1:04d}",
                    user_id=user_id,
                    product_id=product_id,
                    recommendation_type=RecommendationType.COMPLEMENTARY,
                    confidence_score=random.uniform(0.6, 0.85),
                    reasoning="Frequently bought together with your purchases",
                    metadata={"complementarity": random.uniform(0.6, 0.9)},
                    created_date=datetime.now()
                )
                recommendations.append(rec)
                self.recommendations[rec.recommendation_id] = rec
            
            # 3. Trending products in preferred categories
            trending_products = self._find_trending_products(user.preferences, limit=2)
            for product_id in trending_products:
                rec = Recommendation(
                    recommendation_id=f"REC_{len(self.recommendations)+1:04d}",
                    user_id=user_id,
                    product_id=product_id,
                    recommendation_type=RecommendationType.TRENDING,
                    confidence_score=random.uniform(0.5, 0.8),
                    reasoning="Trending in your preferred categories",
                    metadata={"trend_score": random.uniform(0.5, 0.9)},
                    created_date=datetime.now()
                )
                recommendations.append(rec)
                self.recommendations[rec.recommendation_id] = rec
            
            # 4. Price drop alerts
            price_drop_products = self._find_price_drop_products(user, limit=2)
            for product_id in price_drop_products:
                rec = Recommendation(
                    recommendation_id=f"REC_{len(self.recommendations)+1:04d}",
                    user_id=user_id,
                    product_id=product_id,
                    recommendation_type=RecommendationType.PRICE_DROP,
                    confidence_score=random.uniform(0.8, 0.95),
                    reasoning="Price drop alert for items you're interested in",
                    metadata={"price_reduction": random.uniform(0.1, 0.4)},
                    created_date=datetime.now()
                )
                recommendations.append(rec)
                self.recommendations[rec.recommendation_id] = rec
            
            logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")
            
            return recommendations[:self.shopping_config["max_recommendations"]]
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise
    
    def _find_similar_products(self, purchase_history: List[str], limit: int = 5) -> List[str]:
        """Find products similar to purchase history"""
        similar_products = []
        
        for purchased_id in purchase_history[:10]:  # Limit to recent purchases
            if purchased_id in self.products:
                purchased_product = self.products[purchased_id]
                
                # Find products in same category with similar features
                for product_id, product in self.products.items():
                    if (product_id != purchased_id and 
                        product.category == purchased_product.category and
                        product_id not in purchase_history):
                        
                        similarity_score = self._calculate_product_similarity(purchased_product, product)
                        if similarity_score > self.shopping_config["similarity_threshold"]:
                            similar_products.append((product_id, similarity_score))
        
        # Sort by similarity and return top products
        similar_products.sort(key=lambda x: x[1], reverse=True)
        return [product_id for product_id, _ in similar_products[:limit]]
    
    def _calculate_product_similarity(self, product1: Product, product2: Product) -> float:
        """Calculate similarity between two products"""
        score = 0.0
        
        # Category match (high weight)
        if product1.category == product2.category:
            score += 0.4
        
        # Brand match (medium weight)
        if product1.brand == product2.brand:
            score += 0.2
        
        # Price range similarity (medium weight)
        price_diff = abs(product1.price - product2.price) / max(product1.price, product2.price)
        if price_diff < 0.3:
            score += 0.2
        
        # Feature overlap (low weight)
        common_features = set(product1.features) & set(product2.features)
        if common_features:
            score += len(common_features) * 0.1
        
        return min(score, 1.0)
    
    def _find_complementary_products(self, purchase_history: List[str], limit: int = 5) -> List[str]:
        """Find products that complement purchase history"""
        # Define complementary product relationships
        complementary_map = {
            ProductCategory.ELECTRONICS: [ProductCategory.OFFICE, ProductCategory.HEALTH_BEAUTY],
            ProductCategory.CLOTHING: [ProductCategory.HEALTH_BEAUTY, ProductCategory.SPORTS],
            ProductCategory.HOME_GARDEN: [ProductCategory.OFFICE, ProductCategory.AUTOMOTIVE],
            ProductCategory.SPORTS: [ProductCategory.HEALTH_BEAUTY, ProductCategory.TOYS],
            ProductCategory.HEALTH_BEAUTY: [ProductCategory.SPORTS, ProductCategory.CLOTHING]
        }
        
        complementary_products = []
        
        for purchased_id in purchase_history[:5]:
            if purchased_id in self.products:
                purchased_product = self.products[purchased_id]
                complementary_categories = complementary_map.get(purchased_product.category, [])
                
                for product_id, product in self.products.items():
                    if (product.category in complementary_categories and
                        product_id not in purchase_history):
                        complementary_products.append(product_id)
        
        return list(set(complementary_products))[:limit]
    
    def _find_trending_products(self, preferences: Dict, limit: int = 5) -> List[str]:
        """Find trending products in user's preferred categories"""
        trending_products = []
        
        # Get preferred categories from user preferences
        preferred_categories = preferences.get("categories", [ProductCategory.ELECTRONICS])
        
        for category in preferred_categories:
            category_products = [p for p in self.products.values() if p.category == category]
            
            # Sort by ratings and recent additions
            trending = sorted(category_products, 
                            key=lambda x: (x.ratings.average_rating, x.ratings.total_reviews), 
                            reverse=True)
            
            trending_products.extend([p.product_id for p in trending[:2]])
        
        return trending_products[:limit]
    
    def _find_price_drop_products(self, user: UserProfile, limit: int = 5) -> List[str]:
        """Find products with price drops that user might be interested in"""
        price_drop_products = []
        
        # Get products user has browsed or in wishlist
        interested_products = set(user.browsing_history + user.wishlist)
        
        for product_id in interested_products:
            if product_id in self.products:
                product = self.products[product_id]
                
                # Check if there's recent price drop
                if len(product.price_history) >= 2:
                    recent_prices = sorted(product.price_history, key=lambda x: x.date, reverse=True)
                    if len(recent_prices) >= 2:
                        current_price = recent_prices[0].price
                        previous_price = recent_prices[1].price
                        
                        if current_price < previous_price:
                            price_drop_products.append(product_id)
        
        return price_drop_products[:limit]
    
    def _get_market_trends(self) -> Dict:
        """Get current market trends"""
        return {
            "trending_categories": [ProductCategory.ELECTRONICS, ProductCategory.HOME_GARDEN, ProductCategory.HEALTH_BEAUTY],
            "price_trends": {"electronics": "stable", "clothing": "declining", "home": "increasing"},
            "seasonal_factors": ["back_to_school", "holiday_season", "spring_cleaning"],
            "popular_brands": ["Apple", "Samsung", "Nike", "Sony", "Canon"]
        }
    
    def _get_similar_users(self, user: UserProfile) -> List[Dict]:
        """Get similar users based on behavior patterns"""
        similar_users = []
        
        # Find users with similar purchase patterns
        for other_user_id, other_user in self.user_profiles.items():
            if other_user_id != user.user_id:
                similarity = self._calculate_user_similarity(user, other_user)
                if similarity > 0.6:
                    similar_users.append({
                        "user_id": other_user_id,
                        "similarity_score": similarity,
                        "common_interests": list(set(user.preferences.get("categories", [])) & 
                                               set(other_user.preferences.get("categories", [])))
                    })
        
        return sorted(similar_users, key=lambda x: x["similarity_score"], reverse=True)[:5]
    
    def _calculate_user_similarity(self, user1: UserProfile, user2: UserProfile) -> float:
        """Calculate similarity between two users"""
        score = 0.0
        
        # Category preferences overlap
        categories1 = set(user1.preferences.get("categories", []))
        categories2 = set(user2.preferences.get("categories", []))
        category_overlap = len(categories1 & categories2) / len(categories1 | categories2) if categories1 | categories2 else 0
        score += category_overlap * 0.4
        
        # Purchase history overlap
        purchases1 = set(user1.purchase_history)
        purchases2 = set(user2.purchase_history)
        purchase_overlap = len(purchases1 & purchases2) / len(purchases1 | purchases2) if purchases1 | purchases2 else 0
        score += purchase_overlap * 0.3
        
        # Demographics similarity
        if user1.demographics.get("age_group") == user2.demographics.get("age_group"):
            score += 0.1
        if user1.demographics.get("location") == user2.demographics.get("location"):
            score += 0.1
        
        return score
    
    async def search_products(self, query: str, filters: Dict = None, user_id: str = None) -> Dict:
        """Search products with AI-powered search"""
        try:
            # Prepare search context
            search_context = {
                "query": query,
                "filters": filters or {},
                "user_profile": self.user_profiles.get(user_id).dict() if user_id and user_id in self.user_profiles else None,
                "search_history": self._get_user_search_history(user_id) if user_id else [],
                "trending_products": self._get_trending_products()
            }
            
            # Use Brain AI to enhance search
            ai_search_results = await self.brain_ai.enhance_product_search(search_context)
            
            # Perform product search
            search_results = self._perform_product_search(query, filters)
            
            # Apply AI enhancements
            enhanced_results = self._enhance_search_results(search_results, ai_search_results)
            
            # Sort and rank results
            ranked_results = self._rank_search_results(enhanced_results, user_id)
            
            return {
                "query": query,
                "total_results": len(ranked_results),
                "products": ranked_results[:20],  # Limit to top 20
                "filters_applied": filters or {},
                "search_suggestions": self._generate_search_suggestions(query),
                "related_searches": self._get_related_searches(query)
            }
            
        except Exception as e:
            logger.error(f"Error searching products: {str(e)}")
            raise
    
    def _perform_product_search(self, query: str, filters: Dict = None) -> List[Product]:
        """Perform basic product search"""
        results = []
        query_lower = query.lower()
        
        # Search in product names, descriptions, and tags
        for product in self.products.values():
            score = 0
            
            # Name match (highest weight)
            if query_lower in product.name.lower():
                score += 3
            
            # Description match
            if query_lower in product.description.lower():
                score += 2
            
            # Tag match
            if any(query_lower in tag.lower() for tag in product.tags):
                score += 2
            
            # Category match
            if query_lower in product.category.value.lower():
                score += 1
            
            # Brand match
            if query_lower in product.brand.lower():
                score += 1
            
            if score > 0:
                results.append((product, score))
        
        # Apply filters
        if filters:
            results = self._apply_filters(results, filters)
        
        # Sort by relevance score
        results.sort(key=lambda x: x[1], reverse=True)
        
        return [product for product, _ in results]
    
    def _apply_filters(self, results: List[Tuple[Product, float]], filters: Dict) -> List[Tuple[Product, float]]:
        """Apply search filters"""
        filtered_results = []
        
        for product, score in results:
            include = True
            
            # Price range filter
            if "price_min" in filters and product.price < filters["price_min"]:
                include = False
            if "price_max" in filters and product.price > filters["price_max"]:
                include = False
            
            # Category filter
            if "category" in filters and product.category != filters["category"]:
                include = False
            
            # Brand filter
            if "brand" in filters and product.brand not in filters["brand"]:
                include = False
            
            # Rating filter
            if "min_rating" in filters and product.ratings.average_rating < filters["min_rating"]:
                include = False
            
            # Availability filter
            if "availability" in filters and product.availability != filters["availability"]:
                include = False
            
            # Stock filter
            if "in_stock_only" in filters and filters["in_stock_only"] and product.stock_quantity <= 0:
                include = False
            
            if include:
                filtered_results.append((product, score))
        
        return filtered_results
    
    def _enhance_search_results(self, results: List[Product], ai_enhancements: Dict) -> List[Dict]:
        """Enhance search results with AI insights"""
        enhanced_results = []
        
        for product in results:
            enhanced_product = {
                "product": product,
                "relevance_score": random.uniform(0.7, 1.0),
                "ai_insights": {
                    "quality_score": product.ratings.average_rating / 5.0,
                    "value_score": self._calculate_value_score(product),
                    "trend_score": random.uniform(0.3, 0.9),
                    "recommendation_strength": random.uniform(0.4, 0.9)
                },
                "smart_tags": self._generate_smart_tags(product),
                "price_analysis": self._analyze_price(product)
            }
            enhanced_results.append(enhanced_product)
        
        return enhanced_results
    
    def _calculate_value_score(self, product: Product) -> float:
        """Calculate value score for product"""
        # Base score on price vs features
        base_score = len(product.features) / 10.0  # Normalize features
        
        # Adjust for price range
        if product.price < 50:
            base_score *= 1.2  # Good value for low price
        elif product.price > 500:
            base_score *= 0.8  # Premium pricing
        
        # Adjust for ratings
        rating_factor = product.ratings.average_rating / 5.0
        
        return min((base_score * rating_factor), 1.0)
    
    def _generate_smart_tags(self, product: Product) -> List[str]:
        """Generate smart tags for product"""
        tags = []
        
        # Price-based tags
        if product.original_price and product.price < product.original_price:
            tags.append("on_sale")
        
        if product.price < 25:
            tags.append("budget_friendly")
        elif product.price > 200:
            tags.append("premium")
        
        # Rating-based tags
        if product.ratings.average_rating >= 4.5:
            tags.append("highly_rated")
        
        if product.ratings.total_reviews > 100:
            tags.append("popular")
        
        # Category-specific tags
        if product.category == ProductCategory.ELECTRONICS:
            tags.append("tech_gadget")
        elif product.category == ProductCategory.CLOTHING:
            tags.append("fashion")
        elif product.category == ProductCategory.HOME_GARDEN:
            tags.append("home_improvement")
        
        return tags
    
    def _analyze_price(self, product: Product) -> Dict:
        """Analyze product pricing"""
        analysis = {
            "current_price": product.price,
            "price_category": self._categorize_price(product.price),
            "price_trend": "stable",  # Would analyze price history
            "competitiveness": random.choice(["high", "medium", "low"]),
            "savings_potential": 0
        }
        
        if product.original_price:
            savings = product.original_price - product.price
            analysis["original_price"] = product.original_price
            analysis["savings_amount"] = savings
            analysis["savings_percentage"] = (savings / product.original_price) * 100
            analysis["savings_potential"] = savings
        
        return analysis
    
    def _categorize_price(self, price: float) -> str:
        """Categorize price range"""
        if price < 25:
            return "budget"
        elif price < 100:
            return "moderate"
        elif price < 300:
            return "mid_range"
        elif price < 1000:
            return "premium"
        else:
            return "luxury"
    
    def _rank_search_results(self, enhanced_results: List[Dict], user_id: str = None) -> List[Dict]:
        """Rank search results using multiple factors"""
        user = self.user_profiles.get(user_id) if user_id else None
        
        for result in enhanced_results:
            product = result["product"]
            final_score = result["relevance_score"]
            
            # Boost score for user's preferred brands
            if user and product.brand in user.preferences.get("brands", []):
                final_score *= 1.2
            
            # Boost score for highly rated products
            rating_boost = (product.ratings.average_rating - 3) * 0.1
            final_score += rating_boost
            
            # Boost score for in-stock items
            if product.stock_quantity > 0:
                final_score *= 1.1
            
            # Boost score for good value products
            final_score *= result["ai_insights"]["value_score"]
            
            # Boost score for trending products
            final_score *= result["ai_insights"]["trend_score"]
            
            result["final_score"] = min(final_score, 1.0)
        
        # Sort by final score
        enhanced_results.sort(key=lambda x: x["final_score"], reverse=True)
        
        return enhanced_results
    
    def _get_user_search_history(self, user_id: str) -> List[str]:
        """Get user's search history"""
        if user_id in self.shopping_sessions:
            searches = []
            for session in self.shopping_sessions.values():
                if session.user_id == user_id:
                    searches.extend(session.search_queries)
            return searches
        return []
    
    def _get_trending_products(self) -> List[str]:
        """Get trending products"""
        # Sort products by ratings and recency
        trending = sorted(self.products.values(),
                         key=lambda x: (x.ratings.average_rating, x.ratings.total_reviews),
                         reverse=True)
        return [p.product_id for p in trending[:10]]
    
    def _generate_search_suggestions(self, query: str) -> List[str]:
        """Generate search suggestions"""
        suggestions = []
        query_lower = query.lower()
        
        # Generate suggestions based on popular searches
        popular_searches = [
            "wireless headphones", "running shoes", "coffee maker", "laptop computer",
            "skincare products", "workout equipment", "kitchen appliances", "phone case"
        ]
        
        for search in popular_searches:
            if any(word in search for word in query_lower.split()):
                suggestions.append(search)
        
        # Add category-specific suggestions
        for category in ProductCategory:
            if query_lower in category.value:
                suggestions.extend([
                    f"best {category.value} 2024",
                    f"cheap {category.value}",
                    f"reviews {category.value}"
                ])
        
        return suggestions[:5]
    
    def _get_related_searches(self, query: str) -> List[str]:
        """Get related search terms"""
        related = []
        query_lower = query.lower()
        
        # Define related terms mapping
        related_map = {
            "phone": ["smartphone", "mobile", "iphone", "android"],
            "laptop": ["notebook", "computer", "macbook", "ultrabook"],
            "shoes": ["sneakers", "footwear", "running", "boots"],
            "shirt": ["clothing", "apparel", "fashion", "tops"],
            "book": ["reading", "literature", "novel", "textbook"]
        }
        
        for word, related_words in related_map.items():
            if word in query_lower:
                related.extend(related_words)
        
        return list(set(related))[:5]
    
    def get_shopping_dashboard(self, user_id: str = None) -> Dict:
        """Generate comprehensive shopping dashboard"""
        try:
            # User-specific or general dashboard
            if user_id and user_id in self.user_profiles:
                user_dashboard = self._get_user_dashboard(user_id)
            else:
                user_dashboard = self._get_general_dashboard()
            
            # Market overview
            market_overview = self._get_market_overview()
            
            # Trending products
            trending_products = self._get_trending_products_dashboard()
            
            # Category insights
            category_insights = self._get_category_insights()
            
            # Price intelligence
            price_intelligence = self._get_price_intelligence()
            
            # Shopping trends
            shopping_trends = self._get_shopping_trends()
            
            return {
                "user_dashboard": user_dashboard,
                "market_overview": market_overview,
                "trending_products": trending_products,
                "category_insights": category_insights,
                "price_intelligence": price_intelligence,
                "shopping_trends": shopping_trends,
                "recommendations_summary": self._get_recommendations_summary(user_id),
                "insights_summary": self._get_insights_summary(user_id)
            }
            
        except Exception as e:
            logger.error(f"Error generating shopping dashboard: {str(e)}")
            raise
    
    def _get_user_dashboard(self, user_id: str) -> Dict:
        """Get user-specific dashboard"""
        user = self.user_profiles[user_id]
        
        # User stats
        total_purchases = len(user.purchase_history)
        total_spent = sum(self.products[pid].price for pid in user.purchase_history if pid in self.products)
        favorite_categories = list(set(p.category.value for pid in user.purchase_history 
                                     if pid in self.products for p in [self.products[pid]]))
        
        # Recent activity
        recent_sessions = [s for s in self.shopping_sessions.values() 
                          if s.user_id == user_id and s.start_time >= datetime.now() - timedelta(days=7)]
        
        return {
            "user_profile": user.dict(),
            "shopping_stats": {
                "total_purchases": total_purchases,
                "total_spent": total_spent,
                "favorite_categories": favorite_categories[:5],
                "member_since": user.created_date.strftime("%Y-%m-%d"),
                "last_active": user.last_active.strftime("%Y-%m-%d %H:%M")
            },
            "recent_activity": len(recent_sessions),
            "wishlist_items": len(user.wishlist),
            "pending_recommendations": len([r for r in self.recommendations.values() if r.user_id == user_id]),
            "shopping_insights": len([i for i in self.shopping_insights.values() if i.user_id == user_id])
        }
    
    def _get_general_dashboard(self) -> Dict:
        """Get general marketplace dashboard"""
        return {
            "marketplace_stats": {
                "total_products": len(self.products),
                "total_users": len(self.user_profiles),
                "total_sessions": len(self.shopping_sessions),
                "active_today": len([s for s in self.shopping_sessions.values() 
                                   if s.start_time.date() == datetime.now().date()])
            },
            "top_categories": self._get_top_categories(),
            "popular_brands": self._get_popular_brands(),
            "price_ranges": self._get_price_range_distribution()
        }
    
    def _get_market_overview(self) -> Dict:
        """Get market overview statistics"""
        # Calculate category distribution
        category_counts = {}
        for product in self.products.values():
            category_counts[product.category.value] = category_counts.get(product.category.value, 0) + 1
        
        # Calculate average prices by category
        category_prices = {}
        for category in ProductCategory:
            category_products = [p for p in self.products.values() if p.category == category]
            if category_products:
                avg_price = sum(p.price for p in category_products) / len(category_products)
                category_prices[category.value] = avg_price
        
        return {
            "category_distribution": category_counts,
            "average_prices": category_prices,
            "total_catalog_value": sum(p.price for p in self.products.values()),
            "average_rating": sum(p.ratings.average_rating for p in self.products.values()) / len(self.products),
            "new_products_this_month": len([p for p in self.products.values() 
                                          if p.created_date >= datetime.now() - timedelta(days=30)])
        }
    
    def _get_trending_products_dashboard(self) -> List[Dict]:
        """Get trending products for dashboard"""
        trending = sorted(self.products.values(),
                         key=lambda x: (x.ratings.average_rating, x.ratings.total_reviews),
                         reverse=True)[:10]
        
        return [{
            "product_id": p.product_id,
            "name": p.name,
            "price": p.price,
            "rating": p.ratings.average_rating,
            "reviews": p.ratings.total_reviews,
            "category": p.category.value,
            "trend_score": random.uniform(0.7, 1.0)
        } for p in trending]
    
    def _get_category_insights(self) -> Dict:
        """Get category insights"""
        insights = {}
        
        for category in ProductCategory:
            category_products = [p for p in self.products.values() if p.category == category]
            if category_products:
                avg_price = sum(p.price for p in category_products) / len(category_products)
                avg_rating = sum(p.ratings.average_rating for p in category_products) / len(category_products)
                total_reviews = sum(p.ratings.total_reviews for p in category_products)
                
                insights[category.value] = {
                    "product_count": len(category_products),
                    "average_price": avg_price,
                    "average_rating": avg_rating,
                    "total_reviews": total_reviews,
                    "growth_trend": random.choice(["increasing", "stable", "decreasing"])
                }
        
        return insights
    
    def _get_price_intelligence(self) -> Dict:
        """Get price intelligence data"""
        # Calculate price distribution
        prices = [p.price for p in self.products.values()]
        price_ranges = {
            "under_25": len([p for p in prices if p < 25]),
            "25_to_100": len([p for p in prices if 25 <= p < 100]),
            "100_to_300": len([p for p in prices if 100 <= p < 300]),
            "300_to_1000": len([p for p in prices if 300 <= p < 1000]),
            "over_1000": len([p for p in prices if p >= 1000])
        }
        
        # Find best deals
        deals = sorted(self.products.values(),
                      key=lambda x: (x.original_price - x.price) if x.original_price else 0,
                      reverse=True)[:10]
        
        return {
            "price_distribution": price_ranges,
            "best_deals": [{
                "product_id": p.product_id,
                "name": p.name,
                "original_price": p.original_price,
                "current_price": p.price,
                "savings": (p.original_price - p.price) if p.original_price else 0
            } for p in deals if p.original_price],
            "average_market_price": sum(prices) / len(prices),
            "price_competitiveness": random.uniform(0.7, 0.9)
        }
    
    def _get_shopping_trends(self) -> Dict:
        """Get shopping trends analysis"""
        # Analyze recent sessions for trends
        recent_sessions = [s for s in self.shopping_sessions.values() 
                          if s.start_time >= datetime.now() - timedelta(days=7)]
        
        # Popular search terms
        all_searches = []
        for session in recent_sessions:
            all_searches.extend(session.search_queries)
        
        search_frequency = {}
        for search in all_searches:
            search_frequency[search] = search_frequency.get(search, 0) + 1
        
        top_searches = sorted(search_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "weekly_sessions": len(recent_sessions),
            "top_searches": [{"term": term, "frequency": freq} for term, freq in top_searches],
            "conversion_rate": random.uniform(0.15, 0.35),
            "average_session_value": random.uniform(45, 120),
            "cart_abandonment_rate": random.uniform(0.65, 0.80),
            "returning_customer_rate": random.uniform(0.25, 0.45)
        }
    
    def _get_top_categories(self) -> List[Dict]:
        """Get top categories by product count"""
        category_counts = {}
        for product in self.products.values():
            category_counts[product.category.value] = category_counts.get(product.category.value, 0) + 1
        
        return sorted([{"category": cat, "count": count} for cat, count in category_counts.items()],
                     key=lambda x: x["count"], reverse=True)[:5]
    
    def _get_popular_brands(self) -> List[Dict]:
        """Get popular brands by product count"""
        brand_counts = {}
        for product in self.products.values():
            brand_counts[product.brand] = brand_counts.get(product.brand, 0) + 1
        
        return sorted([{"brand": brand, "count": count} for brand, count in brand_counts.items()],
                     key=lambda x: x["count"], reverse=True)[:10]
    
    def _get_price_range_distribution(self) -> Dict:
        """Get price range distribution"""
        prices = [p.price for p in self.products.values()]
        
        return {
            "minimum": min(prices),
            "maximum": max(prices),
            "median": statistics.median(prices),
            "average": sum(prices) / len(prices)
        }
    
    def _get_recommendations_summary(self, user_id: str = None) -> Dict:
        """Get recommendations summary"""
        if user_id:
            user_recommendations = [r for r in self.recommendations.values() if r.user_id == user_id]
        else:
            user_recommendations = list(self.recommendations.values())
        
        return {
            "total_recommendations": len(user_recommendations),
            "by_type": {rt.value: len([r for r in user_recommendations if r.recommendation_type == rt])
                       for rt in RecommendationType},
            "average_confidence": sum(r.confidence_score for r in user_recommendations) / len(user_recommendations) if user_recommendations else 0
        }
    
    def _get_insights_summary(self, user_id: str = None) -> Dict:
        """Get insights summary"""
        if user_id:
            user_insights = [i for i in self.shopping_insights.values() if i.user_id == user_id]
        else:
            user_insights = list(self.shopping_insights.values())
        
        return {
            "total_insights": len(user_insights),
            "by_type": {},
            "potential_savings": sum(sum(ins.potential_savings.values()) for ins in user_insights),
            "high_impact_insights": len([i for i in user_insights if i.impact_level == "high"])
        }

# FastAPI Application
app = FastAPI(title="Shopping Assistant", version="1.0.0")

# Initialize Brain AI Integration
brain_ai = BrainAIIntegration(mode="demo")
shopping_ai = ShoppingAssistantAI(brain_ai)

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Main dashboard page"""
    return HTMLResponse(content=shopping_ai.web_components.render_shopping_dashboard())

@app.get("/api/products")
async def get_products():
    """Get all products"""
    return {"products": list(shopping_ai.products.values())}

@app.get("/api/users")
async def get_users():
    """Get all user profiles"""
    return {"users": list(shopping_ai.user_profiles.values())}

@app.post("/api/recommendations/{user_id}")
async def generate_recommendations_endpoint(user_id: str):
    """Generate personalized recommendations"""
    try:
        recommendations = await shopping_ai.generate_recommendations(user_id)
        return {"recommendations": [r.dict() for r in recommendations]}
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search")
async def search_products_endpoint(search_request: Dict):
    """Search products"""
    try:
        query = search_request.get("query", "")
        filters = search_request.get("filters", {})
        user_id = search_request.get("user_id")
        
        results = await shopping_ai.search_products(query, filters, user_id)
        return results
    except Exception as e:
        logger.error(f"Error searching products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/shopping-dashboard")
async def get_shopping_dashboard(user_id: str = None):
    """Get shopping dashboard data"""
    try:
 shopping_ai.get        dashboard_data =_shopping_dashboard(user_id)
        return dashboard_data
    except Exception as e:
        logger.error(f"Error getting shopping dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/recommendations")
async def get_recommendations(user_id: str = None):
    """Get recommendations"""
    if user_id:
        user_recommendations = [r for r in shopping_ai.recommendations.values() if r.user_id == user_id]
    else:
        user_recommendations = list(shopping_ai.recommendations.values())
    
    return {"recommendations": [r.dict() for r in user_recommendations]}

@app.get("/api/insights")
async def get_shopping_insights(user_id: str = None):
    """Get shopping insights"""
    if user_id:
        user_insights = [i for i in shopping_ai.shopping_insights.values() if i.user_id == user_id]
    else:
        user_insights = list(shopping_ai.shopping_insights.values())
    
    return {"insights": [i.dict() for i in user_insights]}

@app.get("/api/shopping-sessions")
async def get_shopping_sessions():
    """Get shopping sessions"""
    return {"sessions": list(shopping_ai.shopping_sessions.values())}

@app.post("/api/demo/generate-recommendations")
async def generate_demo_recommendations():
    """Generate recommendations for a random demo user"""
    user_ids = list(shopping_ai.user_profiles.keys())
    if not user_ids:
        raise HTTPException(status_code=404, detail="No users available")
    
    user_id = random.choice(user_ids)
    recommendations = await shopping_ai.generate_recommendations(user_id)
    return {"user_id": user_id, "recommendations": [r.dict() for r in recommendations]}

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    logger.info("Starting Shopping Assistant...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")