import { Component, Input, OnInit } from '@angular/core'

import { IssueService } from '../model/rest-services/issue.service'
import { Issue } from '../model/issue/issue'

@Component({
	selector: 'app-issue',
    templateUrl: './issue.component.html',
	styleUrls: ['./issue.component.css'],
	providers: [ IssueService ]
})
export class IssueComponent implements OnInit {

	@Input() issue: Issue;
	viewLink: string;
	editLink: string;

	ngOnInit(): void {
		this.viewLink = this.issue.id
		this.editLink = `/issues/${this.viewLink}/edit`
	}

}
