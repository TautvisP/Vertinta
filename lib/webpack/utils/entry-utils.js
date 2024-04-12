const fs = require('fs');
const path = require('path');

/**
 * Generates entrypoints object according to the path to the module and a list of themes. 
 * Entrypoint for each module is generated for each theme, for example, `chat/default`, `chat/light`, `chat/dark`.
 * @param {string[]} config.appPaths List of paths to modules containing themes.
 * @param {string[]} config.themes List of supported themes.
 * @param {boolean} [config.silent=true] Whether to print logs. 
 * @returns {Object.<string, string>} Webpack entrypoints object, where key is a name 
 * of the entrypoint and value is a path to the entrypoint file.
 */
const generateCSSEntries = (config) => {
    if (typeof config.silent === 'undefined') {
        config.silent = false;
    }

    const { appPaths, themes, silent } = config;

    const generateAppCSSEntries = (appPath) => {
        return themes.reduce((entries, theme) => {
            entries[`${appPath}/${theme}`] = `../dev/${appPath}/css/${theme}/main.scss`;
            return entries;
        }, {});
    };

    const entries = appPaths.reduce((entries, appPath) => {
        return {
            ...entries,
            ...generateAppCSSEntries(appPath),
        };
    }, {});

    if (!silent) {
        console.info('Theme entrypoints generated:', entries);
    }

    return entries;
};

/**
 * Generates entries for copying all assets into the build folder
 * that are not SCSS / SASS files, such as fonts and images. 
 * @param {string} config.rootPath Where to search for a module (Django application) folder.
 * @param {string[]} config.appPaths List of paths to modules containing themes.
 * @param {string[]} config.themes List of supported themes.
 * @param {string[]} [config.defaultAssets=[]] List of asset directories inside default theme folder which 
 * should be reused, if they do not exist in a theme folder.
 * @returns {Object.<string, string>} Webpack copy entrypoint paths.
 */
const generateCopyEntries = (config) => {
    if (typeof config.silent === 'undefined') {
        config.silent = false;
    }

    const entries = [];
    const { rootPath, appPaths, themes, silent } = config;

    const includeMissingAssets = (appPathName, themeName) => {
        if (!Array.isArray(config.defaultAssets)) {
            return;
        }

        config.defaultAssets.forEach((assetName) => {
            const appCSSPath = path.join(rootPath, appPathName, 'css');
            const defaultAssetPath = path.join(appCSSPath, 'default', assetName);
            const themeAssetPath = path.join(appCSSPath, themeName, assetName);

            if (!fs.existsSync(defaultAssetPath) || fs.existsSync(themeAssetPath)) {
                return;
            }

            entries.push({
                from: defaultAssetPath,
                to: path.join(appPathName, themeName, assetName),
                globOptions: { ignore: ['**/*.css', '**/*.scss'] },
                noErrorOnMissing: true,
            });
        });
    };

    appPaths.forEach((appPathName) => {
        themes.forEach((themeName) => {
            const themePath = path.join(rootPath, appPathName, 'css', themeName);

            if (!fs.existsSync(themePath)) {
                return;
            }

            entries.push({
                from: themePath,
                to: path.join(appPathName, themeName),
                globOptions: { ignore: ['**/*.css', '**/*.scss'] },
                noErrorOnMissing: true,
            });

            if (themeName !== 'default') {
                includeMissingAssets(appPathName, themeName);
            }
        });
    });

    if (!silent) {
        const entriesLog = entries.reduce((entriesLog, entry) => {
            entriesLog[entry.from] = entry.to;
            return entriesLog;
        }, {});

        console.info('Copy entries generated:', entriesLog);
    }

    return entries;
};

module.exports = {
    generateCSSEntries,
    generateCopyEntries,
};
