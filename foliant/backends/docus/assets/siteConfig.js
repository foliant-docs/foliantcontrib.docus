const users = [];

// loading config from external json-file
const siteConfJSON = require('./siteConf.json')

const siteConfig = {
  baseUrl: '/', // Base URL for your project */
  colors: {
    primaryColor: '#536f87',
    secondaryColor: '#3a4d5e',
  },
  copyright: `Copyright © ${new Date().getFullYear()} mycompany`,
  favicon: 'img/favicon.ico',
  headerIcon: 'img/favicon.ico',
  headerLinks: [],
  organizationName: 'mycompany',
  projectName: 'test-site',
  tagline: 'A website for testing',
  title: 'Test Site', // Title for your website.
  url: 'https://your-docusaurus-test-site.com', // Your website URL
  ...siteConfJSON // extending config by loaded from siteConf.json
};

module.exports = siteConfig;
