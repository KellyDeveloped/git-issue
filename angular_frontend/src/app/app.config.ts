export let apiUrl: string = "http://localhost:5555/api/v1";

export let issuesUrl: string = `${apiUrl}/issues`;

export let issuePageUrl = (page: number, limit: number) => `${issuesUrl}?page=${page}&limit=${limit}`;

export let specificIssueUrl = (issueID: string) => `${issuesUrl}/${issueID}`;

export let commentUrl = (issue: string) => `${specificIssueUrl(issue)}/comments`;

export let statusIndicatorsUrl = `${apiUrl}/status-indicators`;
