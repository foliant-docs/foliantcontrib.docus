const users = [];

// loading config from external json-file
const siteConfJSON = require('./siteConf.json')

const siteConfig = {
  title: 'Test Site', // Title for your website.
  tagline: 'A website for testing',
  url: 'https://your-docusaurus-test-site.com', // Your website URL
  baseUrl: '/', // Base URL for your project */
  projectName: 'test-site',
  organizationName: 'mycompany',
  headerLinks: [],
  users,
  headerIcon: 'img/favicon.ico',
  footerIcon: 'img/favicon.ico',
  favicon: 'img/favicon.ico',
  colors: {
    primaryColor: '#536f87',
    secondaryColor: '#3a4d5e',
  },
  copyright: `Copyright © ${new Date().getFullYear()} mycompany`,
  highlight: {
    theme: 'default',
  },
  scripts: ['https://buttons.github.io/buttons.js'],
  onPageNav: 'separate',
  cleanUrl: true,
  ogImage: 'img/undraw_online.svg',
  twitterImage: 'img/undraw_tweetstorm.svg',
  ...siteConfJSON // extending config by loaded from siteConf.json
};

module.exports = siteConfig;
