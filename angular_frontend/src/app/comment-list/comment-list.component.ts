import { Component, OnInit, Input } from '@angular/core';

import { IssueService } from '../model/rest-services/issue.service';
import { Issue } from '../model/issue/issue';
import { Comment } from '../model/issue/comment';

@Component({
	selector: 'app-comment-list',
	templateUrl: './comment-list.component.html',
	styleUrls: ['./comment-list.component.css']
})
export class CommentListComponent implements OnInit {

	@Input() issue: Issue;
	comments: Array<Comment>;

	constructor(private issueService: IssueService) { }

	onCreate(e: Comment) {
		this.comments.push(e);
		this.comments.sort((a, b) => {
			if (a.date == b.date) {
				return 0;
			}
			else if (a.date > b.date) {
				return 1;
			}

			return -1;
		})
	}

	ngOnInit() {
		this.issueService.getComments(this.issue, 1, 10).subscribe(res => { this.comments = res; });
	}

}
