const fs = require('fs');
const path = require('path');
const PLUGIN_NAME = 'virtual-entrypoint';
const VirtualModulesPlugin = require('webpack-virtual-modules');

/**
 * Generates default theme entrypoint (`main.scss`) if it does not exist.
 * With the help of this plugin, it's no longer necessary to manually copy
 * `main.scss` file from `css/default` folder into the theme folder. For example,
 * if you want to create a new theme called `dark`, and want to only change colors only,
 * it's enough to (1) create a theme folder, (2) define theme entrypoint in Webpack
 * configuration and (3) create and modify `colors.scss` file for the new theme. 
 */
class VirtualEntrypointInjectorPlugin {
    /**
     * 
     * @param {VirtualModulesPlugin} virtualModulesPlugin Virtual module generator instance.
     * @param {{ matchPattern: RegExp, silent: boolean }} [options={}] options Injector options.
     */
    constructor(virtualModulesPlugin, options = {}) {
        const defaultOptions = { matchPattern: '', silent: false };
        this.userOptions = { ...defaultOptions, ...options };
        this.virtualModulesPlugin = virtualModulesPlugin;
    }

    /**
     * Returns a modified path by replacing the theme name with `default`, 
     * which should point to the default `main.scss` file. 
     * @param {String} path Theme entrypoint path.
     * @returns {String} Modified path from which default `main.scss` source will be read.
     */
    getDefaultEntryPath(path) {
        const pathTokens = path.split('/');
        pathTokens[pathTokens.length - 2] = 'default';
        return pathTokens.join('/');
    }

    /**
     * If defined theme entrypoint does not exist, virtual entrypoint file will be created instead.
     * Virtual file will be created with contents of the default entrypoint, which is expected
     * to always exist.
     * 
     * For example, suppose we have two theme directories:
     * ```
     *     'dev/chat/default/main.scss'
     *     'dev/chat/dark/main.scss'
     * ```
     * 
     * Now, in Webpack configuration, we would have two entrypoints pointing to these
     * directories like this:
     * ```
     *     entry: {
     *         'chat/default': './dev/chat/default/main.scss'
     *         'chat/dark': './dev/chat/dark/main.scss'
     *     }
     * ```
     * If `main.scss` in the second directory does not exist, its virtual equivalent will be created 
     * and it's contents filled with code from `./dev/chat/default/main.scss`. 
     * Then, this file will be passed to the SASS loader.
     * 
     * However, if theme folder (e.g. `./dev/chat/dark`), or any of its parent folders does not exist, 
     * virtual file creation will be skipped.
     * 
     * @param compiler Webpack compiler instance.
     */
    apply(compiler) {
        const logger = compiler.getInfrastructureLogger(PLUGIN_NAME);

        compiler.hooks.compilation.tap('VirtualModuleInjectorPlugin', (compilation) => {
            for (const [entryName, entryValues] of Object.entries(compilation.options.entry)) {
                for (const entryPath of entryValues['import']) {
                    if (fs.existsSync(entryPath) || entryPath.match(this.userOptions.matchPattern) === null) {
                        continue;
                    }

                    if (!fs.existsSync(path.dirname(entryPath))) {
                        !this.userOptions.silent && logger.warn(`
                            Entrypoint ${entryName} -> ${entryPath} does not have a parent directory. 
                            Theme folder ${entryName} will be created automatically.
                        `);

                        fs.mkdirSync(path.dirname(entryPath), { recursive: true });
                        fs.chmodSync(path.dirname(entryPath), '755');
                    }

                    const defaultEntryPath = this.getDefaultEntryPath(entryPath);

                    fs.readFile(defaultEntryPath, 'utf-8', (error, data) => {
                        if (error) {
                            logger.error('Failed reading default entrypoint:', error);
                            return;
                        }

                        this.virtualModulesPlugin.writeModule(entryPath, data);
                    });
                }
            }
        });
    }
}

module.exports = VirtualEntrypointInjectorPlugin;
