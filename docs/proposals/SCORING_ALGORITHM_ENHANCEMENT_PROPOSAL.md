# Scoring Algorithm Enhancement Proposal: SmartTrip Platform
## Self-Learning Recommendation System with Runtime Optimization

**Document Version:** 1.0  
**Date:** January 2026  
**Author:** Senior Development Team  
**Status:** Proposal

---

## Executive Summary

This proposal outlines a comprehensive enhancement strategy for the SmartTrip recommendation scoring algorithm, focusing on three key areas:

1. **Runtime Performance Optimization** - Reduce scoring latency through caching, parallelization, and algorithmic improvements
2. **Score Weights Accuracy** - Implement self-learning algorithms that automatically adjust scoring weights based on user behavior data
3. **Adaptive Learning System** - Use machine learning techniques to continuously improve recommendation quality based on user interactions

**Key Recommendations:**
- **Phase 1:** Implement caching and performance optimizations (2-4 weeks)
- **Phase 2:** Build data collection infrastructure for weight learning (4-6 weeks)
- **Phase 3:** Implement gradient descent-based weight optimization (6-8 weeks)
- **Phase 4:** Add reinforcement learning for real-time adaptation (8-12 weeks)

---

## Table of Contents

1. [Current System Analysis](#current-system-analysis)
2. [Performance Optimization Strategy](#performance-optimization-strategy)
3. [Self-Learning Weight Adjustment](#self-learning-weight-adjustment)
4. [Machine Learning Approaches](#machine-learning-approaches)
5. [Implementation Roadmap](#implementation-roadmap)
6. [Data Requirements](#data-requirements)
7. [Evaluation Metrics](#evaluation-metrics)
8. [Risk Assessment](#risk-assessment)
9. [Cost-Benefit Analysis](#cost-benefit-analysis)

---

## Current System Analysis

### Current Scoring Algorithm

The current recommendation system uses a rule-based scoring algorithm with fixed weights:

```python
SCORING_WEIGHTS = {
    'BASE_SCORE': 30.0,
    'THEME_FULL': 25.0,
    'THEME_PARTIAL': 12.0,
    'THEME_PENALTY': -15.0,
    'DIFFICULTY_PERFECT': 15.0,
    'DURATION_IDEAL': 12.0,
    'DURATION_GOOD': 8.0,
    'BUDGET_PERFECT': 12.0,
    'BUDGET_GOOD': 8.0,
    'BUDGET_ACCEPTABLE': 5.0,
    'STATUS_GUARANTEED': 7.0,
    'STATUS_LAST_PLACES': 15.0,
    'DEPARTING_SOON': 7.0,
    'GEO_DIRECT_COUNTRY': 15.0,
    'GEO_CONTINENT': 5.0,
}
```

### Current Performance Characteristics

**Scoring Performance:**
- Average scoring time: 200-500ms per query
- Candidates scored: Up to 30 trips (min-heap optimization)
- Database queries: 1-2 queries per recommendation request
- Memory usage: Low (heap-based optimization)

**Current Limitations:**
1. **Fixed Weights** - Weights are manually tuned and don't adapt to user behavior
2. **No Learning** - System doesn't improve based on user interactions
3. **Single-threaded Scoring** - All trips scored sequentially
4. **No Caching** - Repeated queries score same trips multiple times
5. **Limited Personalization** - Same weights for all users

### Available Data Infrastructure

**Existing Tracking:**
- `Event` model: Tracks user interactions (clicks, views, bookings)
- `TripInteraction` model: Aggregated metrics (CTR, click counts, dwell time)
- `Session` model: User session tracking with search/click counts
- Analytics endpoints: Daily metrics, top searches, evaluation scenarios

**Available Metrics:**
- Click-through rate (CTR) per trip
- Dwell time on trip pages
- Booking start rate
- Save rate
- Contact rate (WhatsApp/phone)
- Position in results when clicked
- Search-to-click conversion

---

## Performance Optimization Strategy

### 1. Caching Layer

**Objective:** Reduce redundant scoring computations

**Implementation:**
```python
# Cache scored trips for common preference combinations
@lru_cache(maxsize=1000)
def get_cached_score(trip_id, preference_hash):
    # Return pre-computed score if available
    pass

# Cache preference normalization
@lru_cache(maxsize=500)
def normalize_preferences_cached(raw_preferences):
    # Return normalized preferences
    pass
```

**Benefits:**
- 50-70% reduction in scoring time for repeated queries
- Reduced database load
- Lower memory footprint (LRU eviction)

**Cache Strategy:**
- **Trip Scores:** Cache for 1 hour (trip data changes infrequently)
- **Preference Normalization:** Cache for 24 hours
- **Query Results:** Cache for 5 minutes (user may refine search)

### 2. Parallel Scoring

**Objective:** Score multiple trips concurrently

**Implementation:**
```python
from concurrent.futures import ThreadPoolExecutor
import asyncio

async def score_candidates_parallel(candidates, score_func, max_workers=4):
    """Score candidates in parallel using thread pool."""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        scored_trips = await asyncio.gather(*[
            asyncio.to_thread(score_func, occ) 
            for occ in candidates
        ])
    return [trip for trip in scored_trips if trip]
```

**Benefits:**
- 2-4x speedup on multi-core systems
- Better CPU utilization
- Reduced latency for large candidate sets

**Considerations:**
- Thread pool size: 4-8 workers (balance CPU vs memory)
- Database connection pooling: Ensure sufficient connections
- Memory usage: Monitor heap size with parallel execution

### 3. Pre-computed Feature Vectors

**Objective:** Pre-calculate trip features to avoid repeated database queries

**Implementation:**
```python
class TripFeatureVector:
    """Pre-computed trip features for fast scoring."""
    trip_id: int
    theme_tags: List[int]
    difficulty_level: int
    duration_days: int
    price_range: Tuple[float, float]
    country_id: int
    continent: str
    # ... other features
    
# Update feature vectors on trip changes (background job)
def update_feature_vectors():
    """Background job to refresh feature vectors."""
    pass
```

**Benefits:**
- Eliminate database queries during scoring
- 30-50% reduction in scoring time
- Enables batch scoring optimizations

**Storage:**
- Redis cache for hot trips
- Database table for persistent storage
- Background job to refresh daily

### 4. Early Termination Optimization

**Objective:** Skip scoring trips that cannot improve results

**Implementation:**
```python
def score_with_early_termination(candidates, score_func, min_score_threshold):
    """Skip trips that cannot exceed minimum score."""
    heap = []
    current_min_score = min_score_threshold
    
    for occ in candidates:
        # Quick pre-filter: skip if base score too low
        if estimate_min_score(occ) < current_min_score:
            continue
            
        scored_trip = score_func(occ)
        # ... rest of heap logic
```

**Benefits:**
- Reduce unnecessary scoring computations
- 20-30% speedup for large candidate sets
- Better resource utilization

---

## Self-Learning Weight Adjustment

### Problem Statement

Current weights are manually tuned and don't adapt to:
- User behavior patterns
- Seasonal trends
- Trip popularity changes
- User segment preferences

### Solution: Gradient Descent Weight Optimization

**Concept:** Use user click data to learn optimal weights that maximize engagement.

**Mathematical Foundation:**

Given:
- `W = {w1, w2, ..., wn}` - Current weight vector
- `X = {x1, x2, ..., xm}` - Feature vectors for trips
- `y = {y1, y2, ..., ym}` - Binary labels (1 = clicked, 0 = not clicked)
- `score(trip_i) = W · X_i` - Predicted score

**Objective Function:**
```
L(W) = -Σ[y_i * log(σ(score_i)) + (1-y_i) * log(1-σ(score_i))]
```

Where `σ(x) = 1 / (1 + e^(-x))` is the sigmoid function.

**Gradient Update:**
```
W_new = W_old - α * ∇L(W)
```

Where `α` is the learning rate.

### Implementation Architecture

```python
class WeightOptimizer:
    """Gradient descent optimizer for scoring weights."""
    
    def __init__(self, initial_weights, learning_rate=0.01):
        self.weights = initial_weights.copy()
        self.learning_rate = learning_rate
        self.history = []
    
    def compute_gradient(self, training_data):
        """Compute gradient from user interaction data."""
        gradient = {key: 0.0 for key in self.weights.keys()}
        
        for example in training_data:
            trip_features = example['features']
            clicked = example['clicked']
            position = example['position']
            
            # Compute predicted score
            predicted_score = self._compute_score(trip_features)
            predicted_prob = self._sigmoid(predicted_score)
            
            # Weight by position (higher position = more important)
            position_weight = 1.0 / (1.0 + position)
            
            # Compute error
            error = (clicked - predicted_prob) * position_weight
            
            # Update gradient for each feature
            for feature_name, feature_value in trip_features.items():
                if feature_name in self.weights:
                    gradient[feature_name] += error * feature_value
        
        # Average gradient
        n = len(training_data)
        return {key: grad / n for key, grad in gradient.items()}
    
    def update_weights(self, gradient):
        """Update weights using gradient descent."""
        for key in self.weights:
            self.weights[key] -= self.learning_rate * gradient[key]
        
        # Apply constraints (e.g., keep weights in valid range)
        self._apply_constraints()
    
    def _sigmoid(self, x):
        """Sigmoid activation function."""
        return 1.0 / (1.0 + math.exp(-x))
    
    def _apply_constraints(self):
        """Apply constraints to weights (e.g., keep BASE_SCORE >= 0)."""
        if self.weights['BASE_SCORE'] < 0:
            self.weights['BASE_SCORE'] = 0
        # ... other constraints
```

### Training Data Collection

**Data Schema:**
```python
{
    'session_id': str,
    'user_id': Optional[int],
    'search_preferences': Dict,
    'results': [
        {
            'trip_id': int,
            'position': int,  # 0-indexed position in results
            'score': float,
            'features': {
                'theme_match': int,
                'difficulty_match': bool,
                'duration_match': bool,
                'budget_match': bool,
                'status': str,
                'geo_match': str,
                # ... other features
            },
            'clicked': bool,
            'dwell_time': Optional[int],  # seconds
            'converted': bool  # booking started
        }
    ],
    'timestamp': datetime
}
```

**Collection Strategy:**
1. **Real-time Logging:** Log all recommendation requests with results
2. **Event Tracking:** Link clicks to recommendation sessions
3. **Batch Processing:** Daily aggregation of training examples
4. **Data Validation:** Filter out invalid/bot interactions

### Training Pipeline

**Daily Training Job:**
```python
def train_weights_daily():
    """Daily job to retrain weights from recent data."""
    
    # 1. Collect training data (last 30 days)
    training_data = collect_training_data(days=30)
    
    # 2. Filter and validate data
    training_data = filter_valid_examples(training_data)
    
    # 3. Split into train/validation sets
    train_set, val_set = split_data(training_data, test_size=0.2)
    
    # 4. Initialize optimizer
    optimizer = WeightOptimizer(
        initial_weights=current_weights,
        learning_rate=0.01
    )
    
    # 5. Train for N epochs
    for epoch in range(10):
        gradient = optimizer.compute_gradient(train_set)
        optimizer.update_weights(gradient)
        
        # Validate
        val_loss = compute_validation_loss(val_set, optimizer.weights)
        print(f"Epoch {epoch}: Validation loss = {val_loss}")
    
    # 6. A/B test new weights
    if val_loss < current_validation_loss:
        deploy_weights(optimizer.weights)
```

---

## Machine Learning Approaches

### Approach 1: Logistic Regression with Gradient Descent

**Best For:** Initial implementation, interpretable weights

**Pros:**
- Simple to implement
- Interpretable (weights have clear meaning)
- Fast training
- Works well with existing feature engineering

**Cons:**
- Linear model (may miss non-linear patterns)
- Requires feature engineering

**Implementation Complexity:** Low-Medium

### Approach 2: Random Forest

**Best For:** Capturing non-linear patterns, feature importance

**Pros:**
- Handles non-linear relationships
- Feature importance analysis
- Robust to outliers
- No need for feature scaling

**Cons:**
- Less interpretable than linear models
- Slower inference than linear models
- Requires more data

**Implementation Complexity:** Medium

### Approach 3: Neural Network

**Best For:** Complex patterns, large datasets

**Pros:**
- Can learn complex non-linear patterns
- Handles feature interactions automatically
- Scalable to large datasets

**Cons:**
- Black box (hard to interpret)
- Requires large dataset
- More complex to implement
- Slower inference

**Implementation Complexity:** High

### Approach 4: Reinforcement Learning (Contextual Bandits)

**Best For:** Real-time adaptation, exploration-exploitation

**Pros:**
- Adapts in real-time
- Balances exploration vs exploitation
- Can handle changing user preferences
- No need for historical labels

**Cons:**
- Complex to implement
- Requires careful reward design
- May need exploration period

**Implementation Complexity:** High

### Recommended Approach: Hybrid System

**Phase 1:** Start with Logistic Regression (gradient descent)
- Fast to implement
- Interpretable results
- Baseline for comparison

**Phase 2:** Add Random Forest for comparison
- A/B test against logistic regression
- Analyze feature importance
- Identify non-linear patterns

**Phase 3:** Consider Neural Network if data volume grows
- Only if Random Forest shows significant improvement
- Requires 100k+ training examples

**Phase 4:** Add Reinforcement Learning for real-time adaptation
- Fine-tune weights based on immediate feedback
- Handle cold-start problems

---

## Implementation Roadmap

### Phase 1: Performance Optimization (Weeks 1-4)

**Week 1-2: Caching Layer**
- [ ] Implement LRU cache for trip scores
- [ ] Add Redis for distributed caching
- [ ] Cache preference normalization
- [ ] Add cache invalidation logic
- [ ] Performance testing

**Week 3-4: Parallel Scoring**
- [ ] Implement ThreadPoolExecutor for parallel scoring
- [ ] Add async/await support
- [ ] Optimize database connection pooling
- [ ] Load testing
- [ ] Monitor memory usage

**Deliverables:**
- 50% reduction in scoring latency
- Caching infrastructure operational
- Parallel scoring enabled

### Phase 2: Data Collection Infrastructure (Weeks 5-10)

**Week 5-6: Recommendation Logging**
- [ ] Create `RecommendationLog` model
- [ ] Log all recommendation requests
- [ ] Link clicks to recommendation sessions
- [ ] Add position tracking
- [ ] Data validation

**Week 7-8: Feature Extraction**
- [ ] Extract features from trips
- [ ] Create feature vectors
- [ ] Store features in database
- [ ] Background job to refresh features

**Week 9-10: Training Data Pipeline**
- [ ] Aggregate recommendation logs
- [ ] Join with click/event data
- [ ] Create training examples
- [ ] Data quality checks
- [ ] Export to training format

**Deliverables:**
- Complete data collection pipeline
- 30+ days of training data
- Feature extraction system

### Phase 3: Weight Optimization (Weeks 11-18)

**Week 11-12: Gradient Descent Implementation**
- [ ] Implement `WeightOptimizer` class
- [ ] Gradient computation
- [ ] Weight update logic
- [ ] Constraint handling
- [ ] Unit tests

**Week 13-14: Training Pipeline**
- [ ] Daily training job
- [ ] Train/validation split
- [ ] Model evaluation metrics
- [ ] Weight versioning
- [ ] Rollback mechanism

**Week 15-16: A/B Testing Framework**
- [ ] Implement A/B test infrastructure
- [ ] Weight variant management
- [ ] Traffic splitting
- [ ] Metrics collection
- [ ] Statistical significance testing

**Week 17-18: Integration & Testing**
- [ ] Integrate optimized weights into scoring
- [ ] End-to-end testing
- [ ] Performance validation
- [ ] Monitor for regressions

**Deliverables:**
- Self-learning weight system operational
- A/B testing framework
- 10%+ improvement in CTR

### Phase 4: Advanced ML & Real-time Adaptation (Weeks 19-30)

**Week 19-22: Random Forest Model**
- [ ] Implement Random Forest model
- [ ] Feature importance analysis
- [ ] A/B test against logistic regression
- [ ] Model comparison

**Week 23-26: Reinforcement Learning**
- [ ] Implement contextual bandit algorithm
- [ ] Reward function design
- [ ] Exploration strategy
- [ ] Real-time weight updates

**Week 27-30: Production Optimization**
- [ ] Model serving optimization
- [ ] Batch prediction for caching
- [ ] Monitoring and alerting
- [ ] Documentation

**Deliverables:**
- Advanced ML models operational
- Real-time adaptation enabled
- 20%+ improvement in engagement metrics

---

## Data Requirements

### Minimum Data Requirements

**For Logistic Regression:**
- **Training Examples:** 10,000+ recommendation sessions
- **Click Rate:** >5% (need sufficient positive examples)
- **Time Period:** 30+ days (capture seasonal patterns)
- **User Diversity:** 1,000+ unique users

**For Random Forest:**
- **Training Examples:** 50,000+ recommendation sessions
- **Click Rate:** >5%
- **Time Period:** 60+ days
- **User Diversity:** 5,000+ unique users

**For Neural Network:**
- **Training Examples:** 100,000+ recommendation sessions
- **Click Rate:** >5%
- **Time Period:** 90+ days
- **User Diversity:** 10,000+ unique users

### Data Quality Requirements

1. **Completeness:** >95% of sessions have complete feature data
2. **Accuracy:** Click attribution accuracy >99%
3. **Freshness:** Training data updated daily
4. **Balance:** Sufficient positive/negative examples
5. **Diversity:** Coverage across all trip types, themes, regions

### Data Storage

**Recommendation Logs:**
- Estimated size: 1-5 MB per day
- Retention: 90 days (for training)
- Storage: PostgreSQL table with partitioning

**Feature Vectors:**
- Estimated size: 100 KB per trip
- Updates: Daily batch job
- Storage: Redis cache + PostgreSQL backup

**Training Datasets:**
- Estimated size: 50-200 MB per month
- Format: Parquet files
- Storage: Object storage (S3-compatible)

---

## Evaluation Metrics

### Primary Metrics

1. **Click-Through Rate (CTR)**
   - Definition: Clicks / Impressions
   - Target: 10%+ improvement over baseline
   - Measurement: A/B test comparison

2. **Mean Reciprocal Rank (MRR)**
   - Definition: Average of 1/rank for first clicked trip
   - Target: 15%+ improvement
   - Measurement: Offline evaluation

3. **Normalized Discounted Cumulative Gain (NDCG@10)**
   - Definition: Ranking quality metric
   - Target: 0.5+ (good ranking)
   - Measurement: Offline evaluation

### Secondary Metrics

1. **Dwell Time:** Time spent on clicked trips
2. **Conversion Rate:** Booking starts / Clicks
3. **Diversity:** Variety of trips shown to users
4. **Coverage:** Percentage of trips that appear in results
5. **Latency:** Scoring time (should not increase)

### Evaluation Methodology

**Offline Evaluation:**
- Hold-out test set (20% of data)
- Cross-validation (5-fold)
- Statistical significance testing (t-test)

**Online Evaluation:**
- A/B testing framework
- Traffic split: 50/50 or 90/10
- Minimum sample size: 1,000 sessions per variant
- Statistical significance: p < 0.05

**Continuous Monitoring:**
- Daily metrics dashboard
- Alert on metric degradation
- Weekly model retraining
- Monthly model comparison report

---

## Risk Assessment

### Technical Risks

**Risk 1: Overfitting**
- **Probability:** Medium
- **Impact:** High
- **Mitigation:** 
  - Use train/validation/test splits
  - Regularization (L1/L2)
  - Cross-validation
  - Monitor validation metrics

**Risk 2: Data Quality Issues**
- **Probability:** Medium
- **Impact:** High
- **Mitigation:**
  - Data validation pipeline
  - Anomaly detection
  - Manual review of training data
  - Data quality monitoring

**Risk 3: Performance Degradation**
- **Probability:** Low
- **Impact:** Medium
- **Mitigation:**
  - Performance benchmarks
  - Load testing
  - Caching layer
  - Gradual rollout

**Risk 4: Model Drift**
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:**
  - Regular retraining (daily/weekly)
  - Monitor prediction distribution
  - Alert on significant changes
  - A/B testing before deployment

### Business Risks

**Risk 1: User Experience Degradation**
- **Probability:** Low
- **Impact:** High
- **Mitigation:**
  - A/B testing
  - Gradual rollout
  - Quick rollback mechanism
  - User feedback monitoring

**Risk 2: Increased Costs**
- **Probability:** Medium
- **Impact:** Low
- **Mitigation:**
  - Cost monitoring
  - Optimize model complexity
  - Use efficient algorithms
  - Cache aggressively

**Risk 3: Regulatory/Privacy Concerns**
- **Probability:** Low
- **Impact:** High
- **Mitigation:**
  - Anonymize user data
  - Comply with GDPR/privacy laws
  - Clear privacy policy
  - User consent for data usage

---

## Cost-Benefit Analysis

### Implementation Costs

**Development Time:**
- Phase 1 (Performance): 4 weeks (1 developer)
- Phase 2 (Data Collection): 6 weeks (1 developer)
- Phase 3 (Weight Optimization): 8 weeks (1 developer + 0.5 ML engineer)
- Phase 4 (Advanced ML): 12 weeks (1 developer + 1 ML engineer)
- **Total:** 30 weeks (~7.5 months)

**Infrastructure Costs:**
- Redis cache: $20-50/month
- Additional database storage: $10-30/month
- ML training compute: $50-200/month (if using cloud)
- **Total:** $80-280/month

**Maintenance Costs:**
- Daily training jobs: 1 hour/day
- Monitoring and alerts: 2 hours/week
- Model updates: 4 hours/month
- **Total:** ~20 hours/month

### Expected Benefits

**Performance Improvements:**
- 50% reduction in scoring latency
- 30% reduction in database load
- Better user experience (faster results)

**Engagement Improvements:**
- 10-20% increase in CTR
- 15-25% increase in conversion rate
- Better trip discovery (more diverse results)

**Business Impact:**
- Increased bookings (estimated 10-15%)
- Better user satisfaction
- Competitive advantage
- Data-driven decision making

### ROI Calculation

**Assumptions:**
- Current monthly bookings: 100
- Average booking value: $2,000
- Current monthly revenue: $200,000
- Expected improvement: 12% (mid-range estimate)

**Expected Additional Revenue:**
- Additional bookings: 12 per month
- Additional revenue: $24,000/month
- Annual additional revenue: $288,000

**Costs:**
- Development: $60,000 (one-time)
- Infrastructure: $2,000/year
- Maintenance: $30,000/year

**ROI:**
- Year 1: ($288,000 - $60,000 - $2,000 - $30,000) = $196,000
- Year 2+: ($288,000 - $2,000 - $30,000) = $256,000/year
- **Payback Period:** ~3 months

---

## Conclusion

This proposal outlines a comprehensive strategy to enhance the SmartTrip recommendation scoring algorithm through:

1. **Performance optimization** - Reducing latency by 50% through caching and parallelization
2. **Self-learning weights** - Automatically adjusting weights based on user behavior
3. **Machine learning integration** - Using advanced algorithms to improve recommendation quality

The phased approach allows for incremental improvements while minimizing risk. Starting with performance optimizations provides immediate benefits, while the self-learning system builds on existing data infrastructure.

**Key Success Factors:**
- High-quality data collection
- Rigorous A/B testing
- Continuous monitoring
- Gradual rollout

**Expected Outcomes:**
- 10-20% improvement in engagement metrics
- 50% reduction in scoring latency
- Self-improving system that adapts to user behavior
- Strong ROI with payback in ~3 months

---

## Appendix

### A. Feature Engineering Details

**Trip Features:**
- Theme match count (0, 1, 2+)
- Difficulty match (exact, ±1, ±2)
- Duration match (exact, ±4 days, ±7 days)
- Budget match (within, +10%, +20%, over)
- Status (Guaranteed, Last Places, Available)
- Departing soon (within 30 days)
- Geography match (country, continent, none)
- Trip type match
- Price range
- Duration range

**User Features (Future):**
- Historical preferences
- Past bookings
- Click patterns
- Search history

### B. Algorithm Pseudocode

```python
# Gradient Descent Training
def train_weights(training_data, initial_weights, learning_rate=0.01, epochs=10):
    weights = initial_weights.copy()
    
    for epoch in range(epochs):
        gradient = compute_gradient(training_data, weights)
        weights = update_weights(weights, gradient, learning_rate)
        
        # Validate
        val_loss = compute_loss(validation_data, weights)
        print(f"Epoch {epoch}: Loss = {val_loss}")
    
    return weights

def compute_gradient(data, weights):
    gradient = {key: 0.0 for key in weights.keys()}
    
    for example in data:
        features = example['features']
        clicked = example['clicked']
        position = example['position']
        
        # Compute score
        score = sum(weights[k] * features[k] for k in weights.keys())
        prob = sigmoid(score)
        
        # Position weighting
        position_weight = 1.0 / (1.0 + position)
        error = (clicked - prob) * position_weight
        
        # Update gradient
        for feature_name in weights.keys():
            gradient[feature_name] += error * features[feature_name]
    
    # Average
    n = len(data)
    return {k: v / n for k, v in gradient.items()}
```

### C. Monitoring Dashboard Metrics

**Real-time Metrics:**
- Scoring latency (p50, p95, p99)
- Cache hit rate
- Requests per second
- Error rate

**Model Metrics:**
- Current weights (display)
- Weight change over time (graph)
- Training loss (graph)
- Validation loss (graph)
- A/B test results

**Business Metrics:**
- CTR by variant
- Conversion rate by variant
- Revenue impact
- User satisfaction scores

---

**Document End**
