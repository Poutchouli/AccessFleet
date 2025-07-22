export { matchers } from './matchers.js';

export const nodes = [
	() => import('./nodes/0'),
	() => import('./nodes/1'),
	() => import('./nodes/2'),
	() => import('./nodes/3'),
	() => import('./nodes/4'),
	() => import('./nodes/5'),
	() => import('./nodes/6'),
	() => import('./nodes/7'),
	() => import('./nodes/8'),
	() => import('./nodes/9'),
	() => import('./nodes/10'),
	() => import('./nodes/11'),
	() => import('./nodes/12'),
	() => import('./nodes/13'),
	() => import('./nodes/14'),
	() => import('./nodes/15'),
	() => import('./nodes/16'),
	() => import('./nodes/17'),
	() => import('./nodes/18'),
	() => import('./nodes/19'),
	() => import('./nodes/20'),
	() => import('./nodes/21'),
	() => import('./nodes/22'),
	() => import('./nodes/23'),
	() => import('./nodes/24')
];

export const server_loads = [];

export const dictionary = {
		"/": [2],
		"/admin/analytics": [3],
		"/admin/audit": [4],
		"/admin/dashboard": [5],
		"/admin/db-explorer": [6],
		"/admin/forms": [7],
		"/admin/forms/builder": [9],
		"/admin/forms/[id]": [8],
		"/admin/initialize": [10],
		"/admin/new-user": [11],
		"/admin/permissions": [12],
		"/admin/sql-runner": [13],
		"/admin/temp-accounts": [14],
		"/admin/walkthroughs": [15],
		"/admin/walkthroughs/create": [16],
		"/admin/walkthroughs/edit/[id]": [17],
		"/mailboxes": [18],
		"/requests": [19],
		"/requests/new": [21],
		"/requests/[id]": [20],
		"/shared-mailboxes": [22],
		"/test-api": [23],
		"/users": [24]
	};

export const hooks = {
	handleError: (({ error }) => { console.error(error) }),
	
	reroute: (() => {}),
	transport: {}
};

export const decoders = Object.fromEntries(Object.entries(hooks.transport).map(([k, v]) => [k, v.decode]));

export const hash = false;

export const decode = (type, value) => decoders[type](value);

export { default as root } from '../root.svelte';