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
	() => import('./nodes/23')
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
		"/admin/temp-accounts": [13],
		"/admin/walkthroughs": [14],
		"/admin/walkthroughs/create": [15],
		"/admin/walkthroughs/edit/[id]": [16],
		"/mailboxes": [17],
		"/requests": [18],
		"/requests/new": [20],
		"/requests/[id]": [19],
		"/shared-mailboxes": [21],
		"/test-api": [22],
		"/users": [23]
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