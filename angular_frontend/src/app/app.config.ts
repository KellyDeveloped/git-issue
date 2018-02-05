export let apiUrl: string = "http://localhost:5555/api/v1";

export let issuesUrl: string = `${apiUrl}/issues`;

export let specificIssueUrl = (issue: string) => `${issuesUrl}/${issue}`

export let commentUrl = (issue: string) => `${specificIssueUrl(issue)}/comments`
