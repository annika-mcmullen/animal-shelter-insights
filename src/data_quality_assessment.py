# src/data_quality_assessment.py
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import os


class DataQualityAssessment:
    def __init__(self, db_path="data/shelter_data.db"):
        self.db_path = db_path
        self.df = None

    def load_data(self):
        """Load data from database into pandas DataFrame"""
        if not os.path.exists(self.db_path):
            print(f"Database not found at {self.db_path}")
            return False

        try:
            conn = sqlite3.connect(self.db_path)
            self.df = pd.read_sql_query("SELECT * FROM animals", conn)
            conn.close()
            print(f"Loaded {len(self.df)} animals from database")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

    def basic_stats(self):
        """Generate basic statistics about the dataset"""
        if self.df is None:
            print("No data loaded")
            return

        print("\n" + "=" * 50)
        print("📊 BASIC DATASET STATISTICS")
        print("=" * 50)

        print(f"Total Animals: {len(self.df)}")
        print(f"Date Range: {self.df['scraped_at'].min()} to {self.df['scraped_at'].max()}")

        # Species breakdown
        print(f"\nSpecies Distribution:")
        species_counts = self.df['species'].value_counts()
        for species, count in species_counts.items():
            percentage = (count / len(self.df)) * 100
            print(f"  {species}: {count} ({percentage:.1f}%)")

        # Status breakdown
        print(f"\nStatus Distribution:")
        status_counts = self.df['status'].value_counts()
        for status, count in status_counts.items():
            percentage = (count / len(self.df)) * 100
            print(f"  {status}: {count} ({percentage:.1f}%)")

    def completeness_analysis(self):
        """Analyze data completeness for key fields"""
        if self.df is None:
            return

        print("\n" + "=" * 50)
        print("🔍 DATA COMPLETENESS ANALYSIS")
        print("=" * 50)

        # Key fields for our analysis
        key_fields = {
            'Basic Info': ['name', 'species', 'age', 'gender', 'size'],
            'Breed Info': ['breed_primary', 'breed_secondary', 'breed_mixed'],
            'Physical': ['color_primary', 'coat'],
            'Health/Care': ['spayed_neutered', 'house_trained', 'shots_current'],
            'Behavior': ['good_with_children', 'good_with_dogs', 'good_with_cats'],
            'Content': ['description', 'photos'],
            'Location': ['city', 'state', 'organization_id']
        }

        completeness_report = {}

        for category, fields in key_fields.items():
            print(f"\n{category}:")
            category_data = {}

            for field in fields:
                if field in self.df.columns:
                    if field == 'photos':
                        # Special handling for photos (JSON field)
                        non_empty = self.df[field].apply(
                            lambda x: len(json.loads(x)) > 0 if pd.notna(x) and x != '[]' else False
                        ).sum()
                    else:
                        non_empty = self.df[field].notna().sum()

                    percentage = (non_empty / len(self.df)) * 100
                    category_data[field] = percentage

                    status = "Good" if percentage >= 80 else "Caution️" if percentage >= 50 else "Bad"
                    print(f"  {status} {field}: {non_empty}/{len(self.df)} ({percentage:.1f}%)")
                else:
                    print(f"  ❓ {field}: Field not found")

            completeness_report[category] = category_data

        return completeness_report

    def photo_analysis(self):
        """Analyze photo data specifically"""
        if self.df is None:
            return

        print("\n" + "=" * 50)
        print("PHOTO ANALYSIS")
        print("=" * 50)

        # Parse photo data
        photo_counts = []
        animals_with_photos = 0

        for photos_json in self.df['photos']:
            if pd.notna(photos_json) and photos_json != '[]':
                try:
                    photos = json.loads(photos_json)
                    photo_count = len(photos)
                    photo_counts.append(photo_count)
                    if photo_count > 0:
                        animals_with_photos += 1
                except:
                    photo_counts.append(0)
            else:
                photo_counts.append(0)

        self.df['photo_count'] = photo_counts

        print(
            f"Animals with photos: {animals_with_photos}/{len(self.df)} ({(animals_with_photos / len(self.df) * 100):.1f}%)")
        print(f"Average photos per animal: {np.mean(photo_counts):.2f}")
        print(f"Max photos for one animal: {max(photo_counts)}")

        # Photo count distribution
        print(f"\nPhoto Count Distribution:")
        photo_dist = pd.Series(photo_counts).value_counts().sort_index()
        for count, animals in photo_dist.items():
            print(f"  {count} photos: {animals} animals")

    def description_analysis(self):
        """Analyze description data"""
        if self.df is None:
            return

        print("\n" + "=" * 50)
        print("DESCRIPTION ANALYSIS")
        print("=" * 50)

        # Description completeness
        has_description = self.df['description'].notna() & (self.df['description'] != '')
        animals_with_desc = has_description.sum()

        print(
            f"Animals with descriptions: {animals_with_desc}/{len(self.df)} ({(animals_with_desc / len(self.df) * 100):.1f}%)")

        if animals_with_desc > 0:
            # Description length analysis
            desc_lengths = self.df[has_description]['description'].str.len()

            print(f"Description Length Stats:")
            print(f"  Average: {desc_lengths.mean():.0f} characters")
            print(f"  Median: {desc_lengths.median():.0f} characters")
            print(f"  Min: {desc_lengths.min()} characters")
            print(f"  Max: {desc_lengths.max()} characters")

            # Length categories
            short_desc = (desc_lengths < 100).sum()
            medium_desc = ((desc_lengths >= 100) & (desc_lengths < 500)).sum()
            long_desc = (desc_lengths >= 500).sum()

            print(f"\nDescription Length Distribution:")
            print(f"  Short (<100 chars): {short_desc}")
            print(f"  Medium (100-500 chars): {medium_desc}")
            print(f"  Long (>500 chars): {long_desc}")

    def geographic_analysis(self):
        """Analyze geographic distribution"""
        if self.df is None:
            return

        print("\n" + "=" * 50)
        print("GEOGRAPHIC ANALYSIS")
        print("=" * 50)

        # State distribution
        print("State Distribution:")
        state_counts = self.df['state'].value_counts()
        for state, count in state_counts.items():
            percentage = (count / len(self.df)) * 100
            print(f"  {state}: {count} ({percentage:.1f}%)")

        # City distribution (top 10)
        print(f"\nTop Cities:")
        city_counts = self.df['city'].value_counts().head(10)
        for city, count in city_counts.items():
            percentage = (count / len(self.df)) * 100
            print(f"  {city}: {count} ({percentage:.1f}%)")

    def breed_analysis(self):
        """Analyze breed distribution"""
        if self.df is None:
            return

        print("\n" + "=" * 50)
        print("BREED ANALYSIS")
        print("=" * 50)

        # Most common primary breeds by species
        for species in self.df['species'].unique():
            if pd.notna(species):
                species_data = self.df[self.df['species'] == species]
                print(f"\nTop {species.title()} Breeds:")
                breed_counts = species_data['breed_primary'].value_counts().head(10)
                for breed, count in breed_counts.items():
                    percentage = (count / len(species_data)) * 100
                    print(f"  {breed}: {count} ({percentage:.1f}%)")

        # Mixed breed analysis
        mixed_count = self.df['breed_mixed'].sum() if 'breed_mixed' in self.df.columns else 0
        print(f"\nMixed breeds: {mixed_count}/{len(self.df)} ({(mixed_count / len(self.df) * 100):.1f}%)")

    def generate_quality_report(self, output_file=None):
        """Generate complete data quality report"""
        if not self.load_data():
            return

        print("🔍 GENERATING DATA QUALITY REPORT")
        print("=" * 60)

        # Run all analyses
        self.basic_stats()
        completeness = self.completeness_analysis()
        self.photo_analysis()
        self.description_analysis()
        self.geographic_analysis()
        self.breed_analysis()

        # Summary recommendations
        print("\n" + "=" * 50)
        print("RECOMMENDATIONS")
        print("=" * 50)

        recommendations = []

        # Check photo completeness
        animals_with_photos = (self.df['photo_count'] > 0).sum()
        photo_percentage = (animals_with_photos / len(self.df)) * 100

        if photo_percentage < 80:
            recommendations.append(
                f"Only {photo_percentage:.1f}% of animals have photos. Photo analysis will be limited.")

        # Check description completeness
        has_description = self.df['description'].notna() & (self.df['description'] != '')
        desc_percentage = (has_description.sum() / len(self.df)) * 100

        if desc_percentage < 80:
            recommendations.append(
                f"Only {desc_percentage:.1f}% of animals have descriptions. Text analysis will be limited.")

        # Sample size recommendation
        if len(self.df) < 500:
            recommendations.append(
                f"Current sample size ({len(self.df)}) may be too small for robust analysis. Consider collecting 500-1000 animals.")

        # Geographic diversity
        unique_states = self.df['state'].nunique()
        if unique_states < 3:
            recommendations.append(
                f"Data from only {unique_states} state(s). Consider expanding geographic coverage.")

        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")

        if not recommendations:
            print("Data quality looks good for initial analysis!")

        # Save detailed report if requested
        if output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data_quality_report_{timestamp}.txt"
            print(f"\n📄 Detailed report saved to {filename}")


def main():
    """Run data quality assessment"""
    assessment = DataQualityAssessment()
    assessment.generate_quality_report()


if __name__ == "__main__":
    main()