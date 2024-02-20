// Generated using webpack-cli https://github.com/webpack/webpack-cli

const path = require("path");
const CopyWebpackPlugin = require("copy-webpack-plugin");           // Used to copy all UI related assets into "pub"
const MiniCssExtractPlugin = require("mini-css-extract-plugin");    // Used to define CSS output path in "pub".

const isProduction = process.env.NODE_ENV == "production";

const config = {
  entry: {
    parea: ["babel-polyfill", "../dev/parea/js/main.js", "../dev/parea/css/main.scss"],
    rarea: ["babel-polyfill", "../dev/rarea/js/main.js", "../dev/rarea/css/main.scss"],
    osomdemo: ["../dev/modules/demo/js/main.js", "../dev/modules/demo/css/main.scss"]
  },
  output: {
    path: path.resolve(__dirname, "../dev/pub"),
    filename: "[name]/build.js"
  },
  plugins: [
    // Add your plugins here
    // Learn more about plugins from https://webpack.js.org/configuration/plugins/
    // CSS build output
    new MiniCssExtractPlugin({
        filename: "[name]/build.css",
    }),

    // UI assets output
    new CopyWebpackPlugin({
        patterns: [
            // CSS content collection paths
            { from: "../dev/parea/css/", to: "parea/", globOptions: { ignore: ['**/*.scss', '**/*.css'] } },
            { from: "../dev/rarea/css/", to: "rarea/", globOptions: { ignore: ['**/*.scss', '**/*.css'] } },
        ]
    })
  ],
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/i,
        loader: "babel-loader",
      },
      {
        test: /\.s[ac]ss$/i,
        use: [
            { loader: MiniCssExtractPlugin.loader },
            { loader: "css-loader", options: { url: false } },
            { loader: "sass-loader", options: { sassOptions: { outputStyle: "compressed" } } }
        ]        
      },
      {
        test: /\.(eot|svg|ttf|woff|woff2|png|jpg|gif)$/i,
        type: "asset",
      },

      // Add your rules for custom modules here
      // Learn more about loaders from https://webpack.js.org/loaders/
    ],
  },
  resolve: {
    modules: [
      "./lib/node_modules",
    ]
  }
};

module.exports = () => {
  if (isProduction) {
    config.mode = "production";
  } else {
    config.mode = "development";
  }
  return config;
};
