import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SingleIssueComponent } from './single-issue.component';

describe('SingleIssueComponent', () => {
  let component: SingleIssueComponent;
  let fixture: ComponentFixture<SingleIssueComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SingleIssueComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SingleIssueComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
