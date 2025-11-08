import chalk from 'chalk';
import Table from 'cli-table3';

/**
 * Format weather data as ASCII table
 */
export function formatWeather(weatherData) {
  if (!weatherData.success) {
    return chalk.red('Weather data unavailable');
  }

  const table = new Table({
    head: [chalk.cyan('Property'), chalk.cyan('Value')],
    colWidths: [20, 40],
  });

  table.push(
    ['Location', weatherData.location],
    ['Temperature', `${weatherData.current.temperature}°C (feels like ${weatherData.current.feelsLike}°C)`],
    ['Conditions', weatherData.current.description],
    ['Humidity', `${weatherData.current.humidity}%`],
    ['Wind Speed', `${weatherData.current.windSpeed} m/s`],
    ['Pressure', `${weatherData.current.pressure} hPa`]
  );

  let output = '\n' + chalk.bold.blue('☀️  Current Weather') + '\n';
  output += table.toString();

  if (weatherData.forecast && weatherData.forecast.length > 0) {
    const forecastTable = new Table({
      head: [chalk.cyan('Time'), chalk.cyan('Temp'), chalk.cyan('Conditions'), chalk.cyan('Rain %')],
      colWidths: [20, 10, 20, 10],
    });

    weatherData.forecast.forEach(item => {
      forecastTable.push([
        item.datetime,
        `${item.temp}°C`,
        item.description,
        `${item.precipitation}%`,
      ]);
    });

    output += '\n\n' + chalk.bold.blue('📅 Forecast') + '\n';
    output += forecastTable.toString();
  }

  if (weatherData.mock) {
    output += '\n' + chalk.yellow('⚠️  Using mock data - configure Weather API for real data');
  } else if (weatherData.source) {
    output += '\n' + chalk.gray(`\n📡 Data source: ${weatherData.source}`);
  }

  return output;
}

/**
 * Format agricultural data as ASCII table
 */
export function formatAgricultural(agriData) {
  if (!agriData.success) {
    return chalk.red('Agricultural data unavailable');
  }

  const table = new Table({
    head: [chalk.cyan('Property'), chalk.cyan('Value')],
    colWidths: [25, 45],
  });

  const data = agriData.data;

  if (data.soilMoisture !== undefined) {
    table.push(['Soil Moisture', `${data.soilMoisture}%`]);
  }
  if (data.growingSeason) {
    table.push(['Growing Season', data.growingSeason]);
  }
  if (data.yieldForecast) {
    table.push(['Yield Forecast', data.yieldForecast]);
  }
  if (data.recommendedCrops) {
    table.push(['Recommended Crops', data.recommendedCrops.join(', ')]);
  }

  let output = '\n' + chalk.bold.green('🌾 Agricultural Data') + '\n';
  output += table.toString();

  if (data.alerts && data.alerts.length > 0) {
    output += '\n\n' + chalk.bold.yellow('⚠️  Alerts:') + '\n';
    data.alerts.forEach(alert => {
      output += `  • ${alert}\n`;
    });
  }

  if (agriData.mock) {
    output += '\n' + chalk.yellow('⚠️  Using mock data - configure Agriculture API for real data');
  }

  return output;
}

/**
 * Format soil data
 */
export function formatSoil(soilData) {
  if (!soilData.success) {
    return chalk.red('Soil data unavailable');
  }

  const table = new Table({
    head: [chalk.cyan('Property'), chalk.cyan('Value')],
    colWidths: [25, 45],
  });

  const data = soilData.data;
  table.push(
    ['Soil Type', data.soilType || 'N/A'],
    ['pH Level', data.pH || 'N/A'],
    ['Nitrogen', data.nitrogen || 'N/A'],
    ['Phosphorus', data.phosphorus || 'N/A'],
    ['Potassium', data.potassium || 'N/A'],
    ['Organic Matter', data.organicMatter || 'N/A']
  );

  let output = '\n' + chalk.bold.yellow('🌍 Soil Data') + '\n';
  output += table.toString();

  if (data.recommendations && data.recommendations.length > 0) {
    output += '\n\n' + chalk.bold.cyan('💡 Recommendations:') + '\n';
    data.recommendations.forEach(rec => {
      output += `  • ${rec}\n`;
    });
  }

  return output;
}

/**
 * Format search results
 */
export function formatSearchResults(searchData) {
  if (!searchData.success) {
    return chalk.red('Search failed');
  }

  let output = '\n' + chalk.bold.magenta('🔍 Web Search Results') + '\n\n';

  if (searchData.results.summary) {
    output += chalk.white(searchData.results.summary) + '\n\n';
  }

  if (searchData.results.sources && searchData.results.sources.length > 0) {
    output += chalk.bold('Sources:') + '\n';
    searchData.results.sources.forEach((source, idx) => {
      output += chalk.cyan(`${idx + 1}. ${source.title}`) + '\n';
      output += chalk.gray(`   ${source.url}`) + '\n';
      output += `   ${source.snippet}\n\n`;
    });
  }

  if (searchData.mock) {
    output += chalk.yellow('⚠️  Using mock data - configure Poe API for real search results');
  }

  return output;
}

/**
 * Display banner
 */
export function displayBanner() {
  console.log(chalk.bold.cyan(`
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              ✨  Gemini Regional Agent  🌍                ║
║                                                           ║
║         Your AI Assistant with Real-Time Data             ║
║                                                           ║
║    Data Sources: Web Search • Weather • Agriculture       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
  `));
  console.log(chalk.gray('Powered by Google Gemini AI with live web search via Poe\n'));
}

/**
 * Display help menu
 */
export function displayHelp() {
  console.log(chalk.bold.yellow('\n💬 Chat with Gemini - Example Conversations:\n'));

  console.log(chalk.bold.cyan('Weather Questions:'));
  console.log(chalk.gray('  You: ') + chalk.white('What\'s the weather like in London right now?'));
  console.log(chalk.gray('  You: ') + chalk.white('Will it rain in Addis Ababa this week?'));
  console.log(chalk.gray('  You: ') + chalk.white('Should I bring an umbrella tomorrow in Nairobi?'));

  console.log(chalk.bold.cyan('\nAgriculture & Farming:'));
  console.log(chalk.gray('  You: ') + chalk.white('What crops should I plant in March in Ethiopia?'));
  console.log(chalk.gray('  You: ') + chalk.white('Tell me about soil preparation for maize'));
  console.log(chalk.gray('  You: ') + chalk.white('What are drought-resistant crops for East Africa?'));

  console.log(chalk.bold.cyan('\nCurrent Events & Research:'));
  console.log(chalk.gray('  You: ') + chalk.white('What are the latest farming techniques in 2025?'));
  console.log(chalk.gray('  You: ') + chalk.white('Tell me about recent agricultural innovations'));
  console.log(chalk.gray('  You: ') + chalk.white('What\'s the current state of agriculture in Kenya?'));

  console.log(chalk.bold.cyan('\nGeneral Knowledge:'));
  console.log(chalk.gray('  You: ') + chalk.white('What is NDVI and why is it important?'));
  console.log(chalk.gray('  You: ') + chalk.white('Explain crop rotation benefits'));
  console.log(chalk.gray('  You: ') + chalk.white('How does satellite imagery help farmers?'));

  console.log(chalk.bold.cyan('\nCode Generation:'));
  console.log(chalk.gray('  You: ') + chalk.white('Generate a PyQGIS script for satellite processing'));
  console.log(chalk.gray('  You: ') + chalk.white('I need a script to calculate NDVI from Landsat'));

  console.log(chalk.bold.cyan('\n🔧 System Commands:'));
  console.log(chalk.cyan('  help') + '  - Show this help menu');
  console.log(chalk.cyan('  clear') + ' - Clear the screen');
  console.log(chalk.cyan('  exit') + '  - Exit the chat');

  console.log(chalk.yellow('\n✨ How It Works:'));
  console.log(chalk.gray('  • I analyze your question'));
  console.log(chalk.gray('  • I fetch real-time data when needed (web, weather, agriculture)'));
  console.log(chalk.gray('  • I synthesize everything into a clear answer'));
  console.log(chalk.gray('  • Just ask naturally - I handle the rest!'));

  console.log();
}
