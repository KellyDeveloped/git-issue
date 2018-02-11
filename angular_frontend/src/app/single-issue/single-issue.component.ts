import { ActivatedRoute } from '@angular/router';
import { Component, OnInit } from '@angular/core';

import { IssueCacheService } from '../model/services/issue-cache.service'
import { Issue } from '../model/issue/issue'

@Component({
	selector: 'app-single-issue',
	templateUrl: './single-issue.component.html',
	styleUrls: ['./single-issue.component.css']
})
export class SingleIssueComponent implements OnInit {

	issue: Issue;

	constructor(private cacheService: IssueCacheService, private route: ActivatedRoute) { }

	ngOnInit() {
		const id = this.route.snapshot.paramMap.get("id");
		this.cacheService.getIssue(id).subscribe((res) => {
			this.issue = res;
		})
	}

}
