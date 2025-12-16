"""
Generate 100 Realistic User Personas for Evaluation Scenarios
=============================================================

This script generates diverse user personas for testing the recommendation engine.
Each persona has realistic preferences based on their archetype.

Run from backend folder: python scripts/generate_personas.py
"""

import sys
import os
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from faker import Faker
except ImportError:
    print("ERROR: faker library not installed. Run: pip install faker")
    sys.exit(1)

# Initialize Faker for different locales
fake_en = Faker('en_US')
fake_he = Faker('he_IL')
Faker.seed(42)  # For reproducibility
random.seed(42)


# ============================================
# CONSTANTS (Must match seed.py)
# ============================================

# Trip Type IDs (from seed.py)
TRIP_TYPES = {
    'GEOGRAPHIC_DEPTH': 1,
    'CARNIVALS': 2,
    'SAFARI': 3,
    'TRAIN': 4,
    'CRUISES': 5,
    'HIKING': 6,
    'JEEP': 7,
    'SNOWMOBILE': 8,
    'PHOTOGRAPHY': 9,
    'PRIVATE': 10,
}

# Theme Tag IDs (from seed.py)
THEME_TAGS = {
    'CULTURAL': 1,
    'WILDLIFE': 2,
    'EXTREME': 3,
    'FOOD_WINE': 4,
    'BEACH': 5,
    'MOUNTAIN': 6,
    'DESERT': 7,
    'ARCTIC': 8,
    'TROPICAL': 9,
    'HANUKKAH': 11,
}

# Valid continents
CONTINENTS = [
    'Africa',
    'Asia', 
    'Europe',
    'North & Central America',
    'South America',
    'Oceania',
    'Antarctica',
]

# Simulated locations for users
USER_LOCATIONS = [
    {'city': 'Tel Aviv', 'country': 'Israel'},
    {'city': 'Jerusalem', 'country': 'Israel'},
    {'city': 'Haifa', 'country': 'Israel'},
    {'city': 'New York', 'country': 'USA'},
    {'city': 'Los Angeles', 'country': 'USA'},
    {'city': 'London', 'country': 'UK'},
    {'city': 'Berlin', 'country': 'Germany'},
    {'city': 'Paris', 'country': 'France'},
    {'city': 'Amsterdam', 'country': 'Netherlands'},
    {'city': 'Toronto', 'country': 'Canada'},
    {'city': 'Sydney', 'country': 'Australia'},
    {'city': 'Melbourne', 'country': 'Australia'},
]


# ============================================
# ARCHETYPE DEFINITIONS
# ============================================

class PersonaArchetype:
    """Base class for persona archetypes"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def generate_preferences(self) -> Dict[str, Any]:
        """Generate preferences - override in subclasses"""
        raise NotImplementedError
    
    def get_expected_results(self) -> Dict[str, Any]:
        """Get expected results for evaluation"""
        return {
            'expected_min_results': 1,
            'expected_min_top_score': 40,
        }


class StudentBackpacker(PersonaArchetype):
    """Young budget traveler seeking adventure"""
    
    def __init__(self):
        super().__init__(
            "Student Backpacker",
            "Young budget traveler seeking adventure and challenging experiences"
        )
    
    def generate_preferences(self) -> Dict[str, Any]:
        budget = random.randint(2000, 4500)
        duration_base = random.randint(14, 28)
        
        # Students prefer challenging, budget-friendly trips
        type_choices = [
            TRIP_TYPES['HIKING'],
            TRIP_TYPES['JEEP'],
            TRIP_TYPES['GEOGRAPHIC_DEPTH'],
        ]
        theme_choices = [
            THEME_TAGS['EXTREME'],
            THEME_TAGS['MOUNTAIN'],
            THEME_TAGS['CULTURAL'],
        ]
        continent_choices = ['Asia', 'South America', 'Europe']
        
        return {
            'budget': float(budget),
            'preferred_type_id': random.choice(type_choices),
            'preferred_theme_ids': random.sample(theme_choices, k=random.randint(1, 2)),
            'selected_continents': [random.choice(continent_choices)],
            'min_duration': duration_base - 3,
            'max_duration': duration_base + 5,
            'difficulty': 3,  # High difficulty
            'start_date': self._generate_future_date(),
        }
    
    def _generate_future_date(self) -> str:
        days_ahead = random.randint(60, 365)
        future_date = datetime.now() + timedelta(days=days_ahead)
        return future_date.strftime('%Y-%m-%d')
    
    def get_expected_results(self) -> Dict[str, Any]:
        return {
            'expected_min_results': 3,
            'expected_min_top_score': 55,
        }


class LuxuryRetiree(PersonaArchetype):
    """High-budget traveler seeking comfort and culture"""
    
    def __init__(self):
        super().__init__(
            "Luxury Retiree",
            "High-budget traveler seeking comfortable, culturally rich experiences"
        )
    
    def generate_preferences(self) -> Dict[str, Any]:
        budget = random.randint(12000, 25000)
        duration_base = random.randint(10, 18)
        
        type_choices = [
            TRIP_TYPES['CRUISES'],
            TRIP_TYPES['TRAIN'],
            TRIP_TYPES['GEOGRAPHIC_DEPTH'],
        ]
        theme_choices = [
            THEME_TAGS['FOOD_WINE'],
            THEME_TAGS['CULTURAL'],
            THEME_TAGS['BEACH'],
        ]
        continent_choices = ['Europe', 'Asia', 'Oceania']
        
        return {
            'budget': float(budget),
            'preferred_type_id': random.choice(type_choices),
            'preferred_theme_ids': random.sample(theme_choices, k=random.randint(1, 3)),
            'selected_continents': [random.choice(continent_choices)],
            'min_duration': duration_base - 2,
            'max_duration': duration_base + 4,
            'difficulty': 1,  # Easy
            'start_date': self._generate_future_date(),
        }
    
    def _generate_future_date(self) -> str:
        days_ahead = random.randint(90, 300)
        future_date = datetime.now() + timedelta(days=days_ahead)
        return future_date.strftime('%Y-%m-%d')
    
    def get_expected_results(self) -> Dict[str, Any]:
        return {
            'expected_min_results': 5,
            'expected_min_top_score': 65,
        }


class FamilyVacation(PersonaArchetype):
    """Family with children seeking kid-friendly trips"""
    
    def __init__(self):
        super().__init__(
            "Family Vacation",
            "Family with children seeking comfortable, wildlife and beach experiences"
        )
    
    def generate_preferences(self) -> Dict[str, Any]:
        budget = random.randint(10000, 18000)
        duration_base = random.randint(7, 14)
        
        type_choices = [
            TRIP_TYPES['SAFARI'],
            TRIP_TYPES['GEOGRAPHIC_DEPTH'],
            TRIP_TYPES['CRUISES'],
        ]
        theme_choices = [
            THEME_TAGS['WILDLIFE'],
            THEME_TAGS['TROPICAL'],
            THEME_TAGS['BEACH'],
        ]
        continent_choices = ['Africa', 'Asia', 'North & Central America']
        
        # Families prefer summer months (July/August) or Passover (April)
        month = random.choice([4, 7, 8])
        year = 2025 if month > datetime.now().month else 2026
        
        return {
            'budget': float(budget),
            'preferred_type_id': random.choice(type_choices),
            'preferred_theme_ids': random.sample(theme_choices, k=random.randint(2, 3)),
            'selected_continents': [random.choice(continent_choices)],
            'min_duration': duration_base - 2,
            'max_duration': duration_base + 3,
            'difficulty': 1,  # Easy for kids
            'year': str(year),
            'month': str(month),
        }
    
    def get_expected_results(self) -> Dict[str, Any]:
        return {
            'expected_min_results': 3,
            'expected_min_top_score': 60,
        }


class NichePhotographer(PersonaArchetype):
    """Photography enthusiast seeking specific photo opportunities"""
    
    def __init__(self):
        super().__init__(
            "Niche Photographer",
            "Photography enthusiast seeking wildlife and arctic photo opportunities"
        )
    
    def generate_preferences(self) -> Dict[str, Any]:
        budget = random.randint(8000, 15000)
        duration_base = random.randint(10, 16)
        
        theme_choices = [
            THEME_TAGS['WILDLIFE'],
            THEME_TAGS['ARCTIC'],
            THEME_TAGS['MOUNTAIN'],
        ]
        continent_choices = ['Africa', 'Antarctica', 'Europe', 'North & Central America']
        
        return {
            'budget': float(budget),
            'preferred_type_id': TRIP_TYPES['PHOTOGRAPHY'],
            'preferred_theme_ids': random.sample(theme_choices, k=2),
            'selected_continents': [random.choice(continent_choices)],
            'min_duration': duration_base - 3,
            'max_duration': duration_base + 4,
            'difficulty': random.randint(2, 3),
            'start_date': self._generate_future_date(),
        }
    
    def _generate_future_date(self) -> str:
        days_ahead = random.randint(60, 300)
        future_date = datetime.now() + timedelta(days=days_ahead)
        return future_date.strftime('%Y-%m-%d')
    
    def get_expected_results(self) -> Dict[str, Any]:
        return {
            'expected_min_results': 2,
            'expected_min_top_score': 55,
        }


class AdventureSeeker(PersonaArchetype):
    """Thrill-seeker wanting extreme experiences"""
    
    def __init__(self):
        super().__init__(
            "Adventure Seeker",
            "Thrill-seeker wanting extreme jeep or snowmobile experiences"
        )
    
    def generate_preferences(self) -> Dict[str, Any]:
        budget = random.randint(6000, 12000)
        duration_base = random.randint(8, 14)
        
        type_choices = [
            TRIP_TYPES['JEEP'],
            TRIP_TYPES['SNOWMOBILE'],
            TRIP_TYPES['HIKING'],
        ]
        theme_choices = [
            THEME_TAGS['EXTREME'],
            THEME_TAGS['DESERT'],
            THEME_TAGS['ARCTIC'],
            THEME_TAGS['MOUNTAIN'],
        ]
        continent_choices = ['Asia', 'Africa', 'Europe', 'South America']
        
        return {
            'budget': float(budget),
            'preferred_type_id': random.choice(type_choices),
            'preferred_theme_ids': random.sample(theme_choices, k=random.randint(1, 2)),
            'selected_continents': [random.choice(continent_choices)],
            'min_duration': duration_base - 2,
            'max_duration': duration_base + 4,
            'difficulty': random.choice([2, 3]),
            'start_date': self._generate_future_date(),
        }
    
    def _generate_future_date(self) -> str:
        days_ahead = random.randint(45, 250)
        future_date = datetime.now() + timedelta(days=days_ahead)
        return future_date.strftime('%Y-%m-%d')
    
    def get_expected_results(self) -> Dict[str, Any]:
        return {
            'expected_min_results': 3,
            'expected_min_top_score': 55,
        }


class CultureEnthusiast(PersonaArchetype):
    """Culture lover seeking historical and culinary experiences"""
    
    def __init__(self):
        super().__init__(
            "Culture Enthusiast",
            "Culture lover seeking historical sites, festivals, and local cuisine"
        )
    
    def generate_preferences(self) -> Dict[str, Any]:
        budget = random.randint(7000, 14000)
        duration_base = random.randint(10, 16)
        
        type_choices = [
            TRIP_TYPES['GEOGRAPHIC_DEPTH'],
            TRIP_TYPES['CARNIVALS'],
            TRIP_TYPES['TRAIN'],
        ]
        theme_choices = [
            THEME_TAGS['CULTURAL'],
            THEME_TAGS['FOOD_WINE'],
            THEME_TAGS['HANUKKAH'],
        ]
        continent_choices = ['Europe', 'Asia', 'South America']
        
        return {
            'budget': float(budget),
            'preferred_type_id': random.choice(type_choices),
            'preferred_theme_ids': random.sample(theme_choices, k=random.randint(1, 2)),
            'selected_continents': [random.choice(continent_choices)],
            'min_duration': duration_base - 3,
            'max_duration': duration_base + 4,
            'difficulty': random.choice([1, 2]),
            'start_date': self._generate_future_date(),
        }
    
    def _generate_future_date(self) -> str:
        days_ahead = random.randint(60, 300)
        future_date = datetime.now() + timedelta(days=days_ahead)
        return future_date.strftime('%Y-%m-%d')
    
    def get_expected_results(self) -> Dict[str, Any]:
        return {
            'expected_min_results': 4,
            'expected_min_top_score': 60,
        }


class TropicalIslandLover(PersonaArchetype):
    """Beach lover seeking tropical island getaways"""
    
    def __init__(self):
        super().__init__(
            "Tropical Island Lover",
            "Beach lover seeking relaxing tropical island and beach experiences"
        )
    
    def generate_preferences(self) -> Dict[str, Any]:
        budget = random.randint(8000, 16000)
        duration_base = random.randint(7, 12)
        
        type_choices = [
            TRIP_TYPES['GEOGRAPHIC_DEPTH'],
            TRIP_TYPES['CRUISES'],
        ]
        theme_choices = [
            THEME_TAGS['TROPICAL'],
            THEME_TAGS['BEACH'],
        ]
        continent_choices = ['Asia', 'Oceania', 'North & Central America']
        
        return {
            'budget': float(budget),
            'preferred_type_id': random.choice(type_choices),
            'preferred_theme_ids': theme_choices,  # Both tropical and beach
            'selected_continents': [random.choice(continent_choices)],
            'min_duration': duration_base - 2,
            'max_duration': duration_base + 3,
            'difficulty': 1,
            'start_date': self._generate_future_date(),
        }
    
    def _generate_future_date(self) -> str:
        days_ahead = random.randint(60, 250)
        future_date = datetime.now() + timedelta(days=days_ahead)
        return future_date.strftime('%Y-%m-%d')
    
    def get_expected_results(self) -> Dict[str, Any]:
        return {
            'expected_min_results': 4,
            'expected_min_top_score': 60,
        }


class SafariEnthusiast(PersonaArchetype):
    """Wildlife lover seeking African safari experiences"""
    
    def __init__(self):
        super().__init__(
            "Safari Enthusiast",
            "Wildlife lover seeking authentic African safari and wildlife experiences"
        )
    
    def generate_preferences(self) -> Dict[str, Any]:
        budget = random.randint(10000, 20000)
        duration_base = random.randint(10, 14)
        
        theme_choices = [
            THEME_TAGS['WILDLIFE'],
        ]
        # Sometimes add photography interest
        if random.random() > 0.5:
            theme_choices.append(THEME_TAGS['CULTURAL'])
        
        return {
            'budget': float(budget),
            'preferred_type_id': TRIP_TYPES['SAFARI'],
            'preferred_theme_ids': theme_choices,
            'selected_continents': ['Africa'],
            'min_duration': duration_base - 2,
            'max_duration': duration_base + 3,
            'difficulty': 2,
            'start_date': self._generate_future_date(),
        }
    
    def _generate_future_date(self) -> str:
        days_ahead = random.randint(90, 300)
        future_date = datetime.now() + timedelta(days=days_ahead)
        return future_date.strftime('%Y-%m-%d')
    
    def get_expected_results(self) -> Dict[str, Any]:
        return {
            'expected_min_results': 5,
            'expected_min_top_score': 70,
        }


class WinterSportsLover(PersonaArchetype):
    """Snow and ice enthusiast seeking arctic adventures"""
    
    def __init__(self):
        super().__init__(
            "Winter Sports Lover",
            "Snow enthusiast seeking snowmobile and arctic adventures"
        )
    
    def generate_preferences(self) -> Dict[str, Any]:
        budget = random.randint(9000, 18000)
        duration_base = random.randint(7, 12)
        
        type_choices = [
            TRIP_TYPES['SNOWMOBILE'],
            TRIP_TYPES['HIKING'],
        ]
        theme_choices = [
            THEME_TAGS['ARCTIC'],
            THEME_TAGS['EXTREME'],
        ]
        continent_choices = ['Europe', 'North & Central America', 'Antarctica']
        
        # Winter months preferred
        month = random.choice([1, 2, 12])
        year = 2025 if month == 12 else 2026
        
        return {
            'budget': float(budget),
            'preferred_type_id': random.choice(type_choices),
            'preferred_theme_ids': theme_choices,
            'selected_continents': [random.choice(continent_choices)],
            'min_duration': duration_base - 2,
            'max_duration': duration_base + 3,
            'difficulty': random.choice([2, 3]),
            'year': str(year),
            'month': str(month),
        }
    
    def get_expected_results(self) -> Dict[str, Any]:
        return {
            'expected_min_results': 2,
            'expected_min_top_score': 55,
        }


class MinimalInput(PersonaArchetype):
    """User with minimal search criteria"""
    
    def __init__(self):
        super().__init__(
            "Minimal Input User",
            "User providing only duration, testing algorithm defaults"
        )
    
    def generate_preferences(self) -> Dict[str, Any]:
        return {
            'min_duration': 7,
            'max_duration': 14,
        }
    
    def get_expected_results(self) -> Dict[str, Any]:
        return {
            'expected_min_results': 10,
            'expected_min_top_score': 35,
        }


class EdgeCasePoor(PersonaArchetype):
    """Edge case: Very low budget that should yield 0 results"""
    
    def __init__(self):
        super().__init__(
            "Edge Case - Poor Budget",
            "User with budget below all trips, should yield 0 or relaxed results"
        )
    
    def generate_preferences(self) -> Dict[str, Any]:
        return {
            'budget': float(random.randint(500, 999)),
            'selected_continents': ['Europe'],
            'min_duration': 7,
            'max_duration': 14,
            'difficulty': 1,
        }
    
    def get_expected_results(self) -> Dict[str, Any]:
        return {
            'expected_min_results': 0,
            'expected_min_top_score': None,
            'expects_relaxed': True,
        }


class EdgeCaseImpossible(PersonaArchetype):
    """Edge case: Impossible combination (Antarctica + Tropical)"""
    
    def __init__(self):
        super().__init__(
            "Edge Case - Impossible",
            "Antarctica destination with Tropical theme, logically impossible"
        )
    
    def generate_preferences(self) -> Dict[str, Any]:
        return {
            'budget': 15000.0,
            'preferred_theme_ids': [THEME_TAGS['TROPICAL'], THEME_TAGS['BEACH']],
            'selected_continents': ['Antarctica'],
            'min_duration': 10,
            'max_duration': 14,
            'difficulty': 2,
        }
    
    def get_expected_results(self) -> Dict[str, Any]:
        return {
            'expected_min_results': 0,
            'expected_min_top_score': None,
            'expects_relaxed': True,
        }


# ============================================
# PERSONA GENERATOR
# ============================================

class PersonaGenerator:
    """Generates diverse user personas"""
    
    def __init__(self):
        self.archetypes = [
            (StudentBackpacker, 12),      # 12%
            (LuxuryRetiree, 10),          # 10%
            (FamilyVacation, 12),         # 12%
            (NichePhotographer, 8),       # 8%
            (AdventureSeeker, 12),        # 12%
            (CultureEnthusiast, 12),      # 12%
            (TropicalIslandLover, 10),    # 10%
            (SafariEnthusiast, 8),        # 8%
            (WinterSportsLover, 8),       # 8%
            (MinimalInput, 4),            # 4%
            (EdgeCasePoor, 2),            # 2%
            (EdgeCaseImpossible, 2),      # 2%
        ]
        self.persona_id = 0
        self.names_used = set()
    
    def _generate_unique_name(self, archetype: PersonaArchetype) -> str:
        """Generate a unique persona name"""
        attempts = 0
        while attempts < 100:
            if 'Edge Case' in archetype.name:
                name = f"Test Case {self.persona_id + 1}"
            elif 'Family' in archetype.name:
                family_name = fake_en.last_name()
                name = f"The {family_name} Family"
            elif 'Minimal' in archetype.name:
                name = f"Anonymous User {self.persona_id + 1}"
            else:
                first_name = fake_en.first_name()
                name = f"{first_name} the {archetype.name.split()[0]}"
            
            if name not in self.names_used:
                self.names_used.add(name)
                return name
            attempts += 1
        
        return f"Persona {self.persona_id + 1}"
    
    def _generate_location(self) -> Dict[str, str]:
        """Generate a simulated user location"""
        location = random.choice(USER_LOCATIONS)
        return {
            'city': location['city'],
            'country': location['country'],
            'ip': fake_en.ipv4(),
        }
    
    def generate_persona(self, archetype_class: type) -> Dict[str, Any]:
        """Generate a single persona"""
        self.persona_id += 1
        archetype = archetype_class()
        
        name = self._generate_unique_name(archetype)
        preferences = archetype.generate_preferences()
        expected = archetype.get_expected_results()
        
        return {
            'id': self.persona_id,
            'name': name,
            'description': archetype.description,
            'category': self._categorize(archetype),
            'simulated_location': self._generate_location(),
            'preferences': preferences,
            'expected_min_results': expected.get('expected_min_results', 1),
            'expected_min_top_score': expected.get('expected_min_top_score'),
            'expects_relaxed': expected.get('expects_relaxed', False),
        }
    
    def _categorize(self, archetype: PersonaArchetype) -> str:
        """Categorize the persona for filtering"""
        name = archetype.name.lower()
        if 'edge case' in name:
            return 'edge_case'
        elif 'minimal' in name:
            return 'edge_case'
        elif 'safari' in name:
            return 'regional'
        elif 'winter' in name or 'tropical' in name:
            return 'regional'
        elif 'photographer' in name:
            return 'type_specific'
        else:
            return 'core_persona'
    
    def generate_all(self, total: int = 100) -> List[Dict[str, Any]]:
        """Generate all personas"""
        personas = []
        
        for archetype_class, percentage in self.archetypes:
            count = max(1, int(total * percentage / 100))
            for _ in range(count):
                if len(personas) < total:
                    personas.append(self.generate_persona(archetype_class))
        
        # Fill remaining slots with random archetypes
        main_archetypes = [cls for cls, _ in self.archetypes[:9]]  # Exclude edge cases
        while len(personas) < total:
            archetype_class = random.choice(main_archetypes)
            personas.append(self.generate_persona(archetype_class))
        
        return personas[:total]


def main():
    """Main function to generate personas and save to JSON"""
    
    print("\n" + "=" * 70)
    print("GENERATING 100 USER PERSONAS FOR EVALUATION SCENARIOS")
    print("=" * 70 + "\n")
    
    generator = PersonaGenerator()
    personas = generator.generate_all(100)
    
    # Calculate statistics
    categories = {}
    for p in personas:
        cat = p['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"Generated {len(personas)} personas:\n")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    # Output file path
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'scenarios'
    )
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'generated_personas.json')
    
    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(personas, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved to: {output_file}")
    
    # Show sample personas
    print("\n" + "=" * 70)
    print("SAMPLE PERSONAS")
    print("=" * 70)
    
    for p in personas[:5]:
        print(f"\n[{p['id']}] {p['name']}")
        print(f"    Category: {p['category']}")
        print(f"    Description: {p['description']}")
        print(f"    Location: {p['simulated_location']['city']}, {p['simulated_location']['country']}")
        prefs = p['preferences']
        print(f"    Budget: ${prefs.get('budget', 'N/A'):,.0f}" if prefs.get('budget') else "    Budget: N/A")
        print(f"    Difficulty: {prefs.get('difficulty', 'N/A')}")
        print(f"    Expected Results: >= {p['expected_min_results']}")
    
    print("\n" + "=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70 + "\n")
    
    return personas


if __name__ == '__main__':
    main()
