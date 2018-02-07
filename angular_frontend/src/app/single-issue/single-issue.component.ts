import { ActivatedRoute } from '@angular/router';
import { Component, OnInit } from '@angular/core';

import { IssueService } from '../model/rest-services/issue.service'
import { Issue } from '../model/issue/issue'

@Component({
	selector: 'app-single-issue',
	templateUrl: './single-issue.component.html',
	styleUrls: ['./single-issue.component.css'],
	providers: [IssueService]
})
export class SingleIssueComponent implements OnInit {

	issue: Issue;

	constructor(private issueService: IssueService, private route: ActivatedRoute) { }

	ngOnInit() {
		const id = this.route.snapshot.paramMap.get("id")
		this.issueService.getIssue(id).subscribe((res) => {
			this.issue = res.payload
		})
	}

}
