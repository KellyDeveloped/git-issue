import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators, ValidationErrors, AbstractControl } from '@angular/forms';

import { IssueService } from '../model/rest-services/issue.service'
import { Issue } from '../model/issue/issue'
import { GitUser } from '../model/issue/git-user'

@Component({
	selector: 'app-create-issue',
	templateUrl: './create-issue.component.html',
	styleUrls: ['./create-issue.component.css'],
	providers: [IssueService]
})
export class CreateIssueComponent {

	issueForm: FormGroup

	constructor(private fb: FormBuilder, private issueService: IssueService) {
		this.issueForm = this.fb.group({
			summary: new FormControl('', [Validators.required]),
			description: new FormControl(),
			assignee: new FormControl('', [this.emailOrEmpty]),
			reporter: new FormControl('', [this.emailOrEmpty])
		})
	}

	getSummaryErrorMessage(): string {
		return this.issueForm.invalid ? "Summary must not be empty" : ""
	}

	convertFormToIssue(): Issue {
		const rawIssue = this.issueForm.value;
		let issue = <Issue>rawIssue;

		issue.reporter = rawIssue.reporter ? new GitUser(undefined, rawIssue.reporter) : undefined;
		issue.assignee = rawIssue.assignee ? new GitUser(undefined, rawIssue.assignee) : undefined;
		

		return issue;
	}

	submit() {
		if (this.issueForm.invalid) {
			return;
		}

		let issue = this.convertFormToIssue()
		this.issueService.createIssue(issue);
	}

	emailOrEmpty(control: AbstractControl): ValidationErrors | null {
		return control.value === '' ? null : Validators.email(control);
	}

}
