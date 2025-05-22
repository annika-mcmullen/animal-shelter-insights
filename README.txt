# Animal Shelter Insights

A data analysis project aimed at discovering actionable insights to help shelter animals get adopted faster and improve shelter operations.

## Project Overview

This project analyzes animal shelter data to uncover patterns that can help:
- Optimize animal photos and descriptions for faster adoptions
- Identify animals at risk of long shelter stays
- Reduce adoption bias based on breed, age, or appearance
- Provide data-driven recommendations to shelters and rescue organizations

**The Goal**: Move beyond basic statistics (like "labs get adopted more than pits") to generate insights that shelters can actually implement to save more lives.

## Project Status

### Completed Steps (Phase 1: Foundation)
- [x] **Project Setup**: Created organized directory structure with proper virtual environment
- [x] **API Integration**: Successfully connected to Petfinder API with authentication
- [x] **Database Design**: Implemented SQLite database with comprehensive schema for animals and organizations
- [x] **Data Collection Pipeline**: Built automated data collector that can gather animals by location, species, and filters
- [x] **Database Tools**: Created inspection and export utilities for data exploration
- [x] **Initial Data**: Collected sample dataset of 100 animals (50 dogs, 50 cats) from Nashville area
- [x] **Data Validation**: Verified data collection and storage works correctly

### In Progress
- [ ] **Data Quality Assessment**: Analyze completeness and accuracy of collected data
- [ ] **Exploratory Data Analysis**: Initial patterns and insights discovery

### To-Do List

#### Phase 2: Core Analysis (Next 4-6 weeks)
- [ ] **Photo Analysis**
  - [ ] Analyze photo characteristics (lighting, setting, composition) vs adoption speed
  - [ ] Implement computer vision models to categorize photo quality
  - [ ] Study correlation between number of photos and adoption rates
- [ ] **Description Analysis**
  - [ ] NLP analysis of description language and adoption success
  - [ ] Identify words/phrases that help vs hurt adoption chances
  - [ ] Analyze description length and structure impact
- [ ] **Bias Mapping**
  - [ ] Quantify breed preferences and biases across regions
  - [ ] Analyze age, size, and color preferences
  - [ ] Map geographic variation in adoption patterns
- [ ] **Timing Insights**
  - [ ] Seasonal adoption patterns
  - [ ] Optimal days/times for listing animals
  - [ ] Time-to-adoption analysis by animal characteristics

#### Phase 3: Predictive Modeling (4-6 weeks)
- [ ] **Adoption Likelihood Model**: Predict which animals will be adopted quickly vs slowly
- [ ] **Time-to-Adoption Model**: Estimate how long an animal will stay in the shelter
- [ ] **Risk Assessment**: Identify animals at risk of long shelter stays
- [ ] **Model Validation**: Test models on new data and measure accuracy

#### Phase 4: Actionable Deliverables (2-4 weeks)
- [ ] **Shelter Toolkit**: Best practices guide for photos, descriptions, and timing
- [ ] **Interactive Dashboard**: Real-time insights dashboard for shelters
- [ ] **Policy Recommendations**: Data-driven suggestions for reducing bias
- [ ] **Case Studies**: Before/after examples and success stories

#### Phase 5: Impact & Scaling (Ongoing)
- [ ] **Partner with Local Shelters**: Implement recommendations and measure results
- [ ] **Expand Geographic Coverage**: Scale data collection to multiple regions
- [ ] **Research Publication**: Document findings for animal welfare conferences
- [ ] **Open Source Release**: Make tools available to broader shelter community

## Setup Instructions

### Prerequisites
- Python 3.8+
- Petfinder API account (free at https://www.petfinder.com/developers/)

### Installation

1. **Clone and setup project**:
   ```bash
   git clone <your-repo-url>
   cd animal_shelter_insights
   python -m venv shelter_env
   source shelter_env/bin/activate  # On Windows: shelter_env\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure API credentials**:
   ```bash
   # Create .env file with your Petfinder API credentials
   echo "PETFINDER_API_KEY=your_api_key_here" > .env
   echo "PETFINDER_SECRET=your_secret_here" >> .env
   echo "DATABASE_URL=sqlite:///data/shelter_data.db" >> .env
   ```

3. **Initialize database**:
   ```bash
   python src/database.py
   ```

## Usage

### Data Collection

**Collect sample data** (recommended for testing):
```bash
python src/data_collector.py --mode sample --size 100 --location "your_zip_code"
```

**Collect regional data** across multiple cities:
```bash
python src/data_collector.py --mode regional --size 1000
```

**Custom collection** with specific filters:
```bash
python src/data_collector.py --mode custom --location "90210" --size 500
```

### Data Inspection

**View database summary**:
```bash
python src/inspect_database.py
```

**See sample animals**:
```bash
python src/inspect_database.py --action sample --limit 20
```

**Export data to CSV**:
```bash
python src/inspect_database.py --action export
```

### Analysis (Coming Soon)
```bash
# Jupyter notebook for interactive exploration
jupyter notebook notebooks/explore_data.ipynb

# Run photo analysis
python src/photo_analysis.py

# Generate insights report
python src/generate_report.py
```

## Current Dataset

- **Total Animals**: 100 (as of initial collection)
- **Species**: Dogs (50), Cats (50)
- **Location**: Nashville, TN area (50-mile radius)
- **Status**: All adoptable animals
- **Data Points**: 30+ attributes per animal including breed, age, size, photos, descriptions, location

## Technical Architecture

### Database Schema
- **Animals Table**: Core animal data with 30+ attributes
- **Organizations Table**: Shelter/rescue information
- **Future Tables**: Adoption outcomes, photo analysis results

### Key Components
- **API Client** (`petfinder_api.py`): Handles Petfinder API authentication and data retrieval
- **Database Manager** (`database.py`): SQLAlchemy models and data persistence
- **Data Collector** (`data_collector.py`): Automated data collection with filtering
- **Inspector** (`inspect_database.py`): Database exploration and export utilities

### Tech Stack
- **Data**: Petfinder API, SQLite/PostgreSQL
- **Analysis**: Pandas, NumPy, Scikit-learn
- **NLP**: NLTK, spaCy
- **Computer Vision**: OpenCV, PIL
- **Visualization**: Matplotlib, Seaborn, Plotly
- **Web Dashboard**: React/Flask (planned)

## Expected Impact

### For Shelters
- Increase adoption rates by 15-30% through optimized presentations
- Reduce average time-to-adoption by identifying effective strategies
- Better resource allocation based on predictive models
- Reduced bias against certain breeds or characteristics

### For Animals
- Faster placements in permanent homes
- Reduced stress from long shelter stays
- More successful long-term adoptions through better matching

### For the Field
- Evidence-based best practices for animal welfare
- Open-source tools other shelters can use
- Research contributing to broader animal welfare knowledge

## Contributing

This project welcomes contributions! Areas where help is especially needed:
- Web development for dashboard creation
- Partnerships with shelters for impact validation

## License

MIT License - Feel free to use this code to help animals in need!

## 📞 Contact

**Project Maintainer**: Annika McMullen
**Email**: annikamcmullen@icloud.com
**Purpose**: Helping shelter animals find homes faster through data science

---

*"The greatness of a nation and its moral progress can be judged by the way its animals are treated." - Mahatma Gandhi*

## Additional Resources

- [Petfinder API Documentation](https://www.petfinder.com/developers/v2/docs/)