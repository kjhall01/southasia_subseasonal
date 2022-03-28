# Probabilistic Subseasonal-To-Seasonal (S2S) Precipitation Forecasts for South Asia

***by Kyle Hall & Nachiketa Acharya, 2022***
A case study using XCast to generate probabilistic forecasts of S2S-scale (Aggregated over Weeks 3&4) Indian Summer Monsoon Rainfall (ISMR) by creating Probabilistic Output Extreme Learning Machine (POELM)-based multi-member ensembles of the ECMWF's General Circulation Model. ISMR is characterized by intense rain over India onsetting around June, and receeding around September. For the purposes of this study we take aggregated ECMWF model output at lead times between day 14 and day 28, at initializations for which this target period falls between June 1 and September 30, as predictors. Initializations are also limited to 1/week by selecting only thursdays.  Aggregated High-Resolution India Meteorological Department Daily Precipitation data for the corresponding target periods are used as the predictand. 

We proceed by one-hot encoding the predictand using a scheme which translates the lowest 33% of data points to the "Below Normal" category, the highest 33% of data points to the "Above Normal" category, and all others to the "Near Normal" category. One-Hot encoding is done separately at each week-in-year, to prevent intra-season variability from producing spuriously high skill. The predictors are derived from the ECMWF ensemble members- here we take the minimum, maximum, mean, and standard deviation of the ensemble as predictors. We also use a fifth predictor- a simple "week-in-season" index, with 0 corresponding approximately to the first two weeks of May, and the highest value corresponding to the last two weeks of September. The index increments by one for each target period.  These predictors are then scaled to the interval [-1, 1] using MinMax Scaling, and a set of N randomly-initialized POELM models are fit, and used to make predictions. The N randomly-initialized results are then averaged to create an ensemble mean and address the non-determinism of the POELM approach. 

All of the above operations are performed on a gridpoint-wise basis, and within Leave-One-Year-Out cross-validation. Cross-validated hindcasts are compared with the observations data to compute skill scores. 

# Installing this repository: 

```
git clone https://github.com/kjhall01/southasia_subseasonal.git
cd southasia_subseasonal
conda create -c conda-forge -c hallkjc01 -n climate xcast xarray matplotlib pandas numpy cartopy jupyter
conda activate climate 
python -m ipykernel install --user --name=climate
jupyter notebook SouthAsiaS2S.ipynb
```

select kernel >> climate
then click "restart and run all cells" 

# Results
![generalized ROC & RPSS]()

