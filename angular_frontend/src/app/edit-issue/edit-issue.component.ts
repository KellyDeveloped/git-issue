import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, FormControl, FormGroup, Validators, ValidationErrors, AbstractControl } from '@angular/forms';
import { MatDialog } from '@angular/material';

import { IssueService } from '../model/rest-services/issue.service';
import { IssueCacheService } from '../model/services/issue-cache.service';
import { Issue } from '../model/issue/issue';
import { GitUser } from '../model/issue/git-user';
import { ErrorDialogueComponent } from '../error-dialogue/error-dialogue.component';


@Component({
	selector: 'app-edit-issue',
	templateUrl: './edit-issue.component.html',
	styleUrls: ['./edit-issue.component.css'],
	providers: [IssueService]
})
export class EditIssueComponent implements OnInit {

	issue: Issue;
	currentUser: GitUser;
	statusIndicators: Array<string> = ["open", "closed"] // Constant defaults, safe assumption.

	issueForm: FormGroup;
	showSpinner = false;

	constructor(private fb: FormBuilder,
				private router: Router,
				private dialogue: MatDialog,
				private issueService: IssueService,
				private cacheService: IssueCacheService,
				private route: ActivatedRoute) {
		this.issueForm = this.fb.group({
			summary: new FormControl('', [Validators.required]),
			description: new FormControl(),
			assignee: new FormControl('', [this.emailOrEmpty]),
			reporter: new FormControl('', [this.emailOrEmpty]),
			subscribed: new FormControl(),
			status: new FormControl('', [Validators.required])
		});
	}

	getSummaryErrorMessage(): string {
		return this.issueForm.invalid ? "Summary must not be empty" : ""
	}

	convertFormToIssue(): Issue {
		const rawIssue = this.issueForm.value;

		// Cast the raw values of the form to an issue then correct the values. Hacky? Yes. Quick and easy? Yes.
		let issue = <Issue>rawIssue;
		issue.id = this.issue.id;
		issue.date = this.issue.date;

		issue.reporter = rawIssue.reporter ? new GitUser(undefined, rawIssue.reporter) : undefined;
		issue.assignee = rawIssue.assignee ? new GitUser(undefined, rawIssue.assignee) : undefined;

		issue.subscribers = this.issue.subscribers;

		if (rawIssue.subscribed && !this.isCurrentUserSubscribed()) {
			issue.subscribers.push(this.currentUser);
		}
		else if (!rawIssue.subscribed && this.isCurrentUserSubscribed()) {
			issue.subscribers = issue.subscribers.filter((x) => x.email !== this.currentUser.email);
		}

		return issue;
	}

	submit() {
		if (this.issueForm.invalid) {
			return;
		}

		let issue = this.convertFormToIssue()
		this.cacheService.editIssue(issue).subscribe(res => {
			this.router.navigate([`/issues/${res.payload.id}`])
		}, this.errorFunc);
		this.showSpinner = true;
	}

	emailOrEmpty(control: AbstractControl): ValidationErrors | null {
		return control.value === '' ? null : Validators.email(control);
	}

	isCurrentUserSubscribed() {
		if (this.issue && this.currentUser) {
			return this.issue.subscribers.map(i => i.email).includes(this.currentUser.email);
		}
		return false;
	}

	errorFunc(err) {
		this.dialogue.open(ErrorDialogueComponent, {
			'data': err
		});
		this.issue = new Issue();
		this.showSpinner = false;
	};

	ngOnInit(): void {
		const id = this.route.snapshot.paramMap.get("id");

		this.issueService.getStatusIndicators().subscribe(res => this.statusIndicators = res, this.errorFunc);
		this.cacheService.getIssue(id).subscribe((res) => {
			this.issue = res;
			this.currentUser = this.cacheService.currentUser;

			this.issueForm.get('summary').setValue(this.issue.summary);
			this.issueForm.get('description').setValue(this.issue.description);

			if (this.issue.assignee) {
				this.issueForm.get('assignee').setValue(this.issue.assignee.email);
			}
			if (this.issue.reporter) {
				this.issueForm.get('reporter').setValue(this.issue.reporter.email);
			}

			this.issueForm.get('subscribed').setValue(this.isCurrentUserSubscribed());

			this.issueForm.get('status').setValue(this.issue.status);
		}, this.errorFunc);

	}

}
