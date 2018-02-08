import { Component, OnInit, Input } from '@angular/core';

import { Issue } from '../model/issue/issue';

@Component({
  selector: 'app-issue-list-entry',
  templateUrl: './issue-list-entry.component.html',
  styleUrls: ['./issue-list-entry.component.css']
})
export class IssueListEntryComponent implements OnInit {

	@Input() issue: Issue;
	viewLink: string;
	editLink: string;

	ngOnInit(): void {
		//this.viewLink = this.issue.id
		//this.editLink = `${this.viewLink}/edit`
	}

}
