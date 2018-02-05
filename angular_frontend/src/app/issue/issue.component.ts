import { Component, Input } from '@angular/core'

import { IssueService } from '../model/rest-services/issue.service'
import { Issue } from '../model/issue/issue'

@Component({
	selector: 'app-issue',
    templateUrl: './issue.component.html',
	styleUrls: ['./issue.component.css'],
	providers: [ IssueService ]
})
export class IssueComponent {

	@Input() issue: Issue;

}
