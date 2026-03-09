// Leeds Forest Change Analysis (2000-2024)
// Using Hansen Global Forest Change dataset

// Study area: Leeds bounding box
var leeds = ee.Geometry.Rectangle([-1.8, 53.7, -1.3, 53.9]);

Map.centerObject(leeds, 11);
Map.addLayer(leeds, {color: 'red'}, 'Leeds boundary', false);

// Load Hansen Global Forest Change v1.12 (2000-2024)
var hansen = ee.Image('UMD/hansen/global_forest_change_2024_v1_12');

print('Hansen dataset:', hansen.bandNames());

// Extract relevant bands
var treecover2000 = hansen.select('treecover2000').clip(leeds); // Tree cover in year 2000 (%)
var gain = hansen.select('gain').clip(leeds); // Forest gain 2000-2024 (binary: 1=gain, 0=no gain)
var lossyear = hansen.select('lossyear').clip(leeds); // Year of forest loss (0-24 for 2000-2024)

// Visualize
var treecoverVis = {min: 0, max: 100, palette: ['black', 'green']};
var gainVis = {min: 0, max: 1, palette: ['white', 'blue']};
var lossVis = {min: 0, max: 24, palette: ['yellow', 'red']};

Map.addLayer(treecover2000, treecoverVis, 'Tree cover 2000', false);
Map.addLayer(gain, gainVis, 'Forest gain (2000-2024)', false);
Map.addLayer(lossyear, lossVis, 'Forest loss year', false);

// Calculate annual forest loss area
var years = ee.List.sequence(1, 24); // Hansen codes: 1=2001, 2=2002, ..., 24=2024

var annualLoss = years.map(function(year) {
  var yearMask = lossyear.eq(year); // Pixels lost in this year
  
  // Calculate area (in hectares)
  var lossArea = yearMask.multiply(ee.Image.pixelArea()).divide(10000); // Convert m² to hectares
  
  var stats = lossArea.reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: leeds,
    scale: 30,
    maxPixels: 1e9
  });
  
  return ee.Feature(null, {
    'year': ee.Number(2000).add(year),
    'forest_loss_ha': stats.get('lossyear')
  });
});

var annualLossFC = ee.FeatureCollection(annualLoss);
print('Annual forest loss (hectares):', annualLossFC);

// Calculate total forest gain area
var gainArea = gain.multiply(ee.Image.pixelArea()).divide(10000);

var gainStats = gainArea.reduceRegion({
  reducer: ee.Reducer.sum(),
  geometry: leeds,
  scale: 30,
  maxPixels: 1e9
});

print('Total forest gain 2000-2024 (hectares):', gainStats.get('gain'));

// Calculate baseline tree cover (year 2000)
var treecoverArea = treecover2000.gte(10) // Pixels with ≥10% tree cover
  .multiply(ee.Image.pixelArea())
  .divide(10000);

var treecoverStats = treecoverArea.reduceRegion({
  reducer: ee.Reducer.sum(),
  geometry: leeds,
  scale: 30,
  maxPixels: 1e9
});

print('Baseline tree cover 2000 (hectares):', treecoverStats.get('treecover2000'));

// Calculate net change
var netChange = ee.Number(gainStats.get('gain'))
  .subtract(annualLossFC.aggregate_sum('forest_loss_ha'));

print('Net forest change 2000-2024 (hectares):', netChange);

// Export annual loss data
Export.table.toDrive({
  collection: annualLossFC,
  description: 'Leeds_Annual_Forest_Loss_2001_2024',
  fileFormat: 'CSV'
});

// Create visualization: gain (blue) and loss (red) overlaid
var lossRed = lossyear.gt(0).selfMask().visualize({palette: ['red']});
var gainBlue = gain.selfMask().visualize({palette: ['blue']});

Map.addLayer(lossRed, {}, 'Forest Loss (red)', true);
Map.addLayer(gainBlue, {}, 'Forest Gain (blue)', true);

print('Script complete. Check Tasks tab to export CSV.');